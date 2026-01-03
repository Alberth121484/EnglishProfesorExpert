import hmac
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_db
from app.schemas import TelegramAuthData, TokenResponse
from app.services import StudentService

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()
security = HTTPBearer()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def verify_telegram_auth(auth_data: TelegramAuthData) -> bool:
    """Verify Telegram login widget authentication."""
    # Create data check string
    data_check = "\n".join([
        f"auth_date={auth_data.auth_date}",
        f"first_name={auth_data.first_name}",
        f"id={auth_data.id}",
    ])
    
    if auth_data.last_name:
        data_check = f"last_name={auth_data.last_name}\n" + data_check
    if auth_data.username:
        data_check = f"username={auth_data.username}\n" + data_check
    if auth_data.photo_url:
        data_check = f"photo_url={auth_data.photo_url}\n" + data_check
    
    # Sort and join
    check_list = sorted(data_check.split("\n"))
    data_check_string = "\n".join(check_list)
    
    # Calculate hash
    secret_key = hashlib.sha256(settings.telegram_bot_token.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Verify hash and check auth_date is not too old (1 day)
    auth_time = datetime.fromtimestamp(auth_data.auth_date, tz=timezone.utc)
    is_recent = (datetime.now(timezone.utc) - auth_time) < timedelta(days=1)
    
    return calculated_hash == auth_data.hash and is_recent


def create_access_token(telegram_id: int, student_id: int) -> str:
    """Create JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(telegram_id),
        "student_id": student_id,
        "exp": expire
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


async def get_current_student_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Get current student ID from JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[ALGORITHM]
        )
        student_id = payload.get("student_id")
        if student_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return student_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/telegram", response_model=TokenResponse)
async def authenticate_telegram(
    auth_data: TelegramAuthData,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user via Telegram Login Widget."""
    # For development, skip verification if debug mode
    if not settings.debug and not verify_telegram_auth(auth_data):
        raise HTTPException(status_code=401, detail="Invalid Telegram authentication")
    
    student_service = StudentService(db)
    student, _ = await student_service.get_or_create_student(
        telegram_id=auth_data.id,
        first_name=auth_data.first_name,
        last_name=auth_data.last_name,
        username=auth_data.username
    )
    
    token = create_access_token(auth_data.id, student.id)
    
    return TokenResponse(
        access_token=token,
        student_id=student.id
    )


@router.post("/telegram-id/{telegram_id}", response_model=TokenResponse)
async def authenticate_by_telegram_id(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate by Telegram ID (for users coming from bot).
    Creates the student automatically if they don't exist yet.
    """
    logger.info(f"Auth attempt for telegram_id: {telegram_id}")
    
    student_service = StudentService(db)
    
    # Get or create student - this ensures users can always access the panel
    student, is_new = await student_service.get_or_create_student(
        telegram_id=telegram_id,
        first_name="Usuario",  # Default name, will be updated when they use the bot
        last_name=None,
        username=None
    )
    
    if is_new:
        logger.info(f"Created new student on panel access: {student.id} (telegram_id: {telegram_id})")
    else:
        logger.info(f"Found existing student: {student.id} - {student.first_name}")
    
    token = create_access_token(telegram_id, student.id)
    
    return TokenResponse(
        access_token=token,
        student_id=student.id
    )
