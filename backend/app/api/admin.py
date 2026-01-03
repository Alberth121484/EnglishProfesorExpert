"""Admin API endpoints for statistics and user management."""
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models import Student, Lesson, LessonMessage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# ============ Pydantic Models ============

class OverviewStats(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    new_users_today: int
    new_users_week: int
    new_users_month: int
    total_lessons: int
    total_messages: int
    avg_lessons_per_user: float
    avg_streak_days: float


class UserActivity(BaseModel):
    user_id: int
    telegram_id: int
    name: str
    username: str | None
    level: str
    total_lessons: int
    streak_days: int
    last_activity: datetime | None
    registered_at: datetime
    is_active: bool
    days_since_last_activity: int


class UsageByLevel(BaseModel):
    level: str
    user_count: int
    percentage: float


class DailyStats(BaseModel):
    date: str
    new_users: int
    active_users: int
    lessons_count: int
    messages_count: int


class TokenUsage(BaseModel):
    user_id: int
    name: str
    estimated_tokens: int
    estimated_cost_usd: float
    messages_count: int


class ChurnedUser(BaseModel):
    user_id: int
    telegram_id: int
    name: str
    last_activity: datetime | None
    days_inactive: int
    total_lessons: int
    level: str


class EngagementStats(BaseModel):
    avg_session_duration_minutes: float
    avg_messages_per_session: float
    avg_daily_usage_minutes: float
    retention_rate_7d: float
    retention_rate_30d: float
    churn_rate: float


# ============ API Endpoints ============

@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """Get overview statistics for the dashboard."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Total users
    total_users = await db.scalar(select(func.count(Student.id)))
    
    # Active users (by last_activity)
    active_today = await db.scalar(
        select(func.count(Student.id)).where(Student.last_activity >= today_start)
    )
    active_week = await db.scalar(
        select(func.count(Student.id)).where(Student.last_activity >= week_ago)
    )
    active_month = await db.scalar(
        select(func.count(Student.id)).where(Student.last_activity >= month_ago)
    )
    
    # New users
    new_today = await db.scalar(
        select(func.count(Student.id)).where(Student.registered_at >= today_start)
    )
    new_week = await db.scalar(
        select(func.count(Student.id)).where(Student.registered_at >= week_ago)
    )
    new_month = await db.scalar(
        select(func.count(Student.id)).where(Student.registered_at >= month_ago)
    )
    
    # Lessons and messages
    total_lessons = await db.scalar(select(func.count(Lesson.id))) or 0
    total_messages = await db.scalar(select(func.count(LessonMessage.id))) or 0
    
    # Averages
    avg_lessons = total_lessons / total_users if total_users > 0 else 0
    avg_streak = await db.scalar(select(func.avg(Student.streak_days))) or 0
    
    return OverviewStats(
        total_users=total_users or 0,
        active_users_today=active_today or 0,
        active_users_week=active_week or 0,
        active_users_month=active_month or 0,
        new_users_today=new_today or 0,
        new_users_week=new_week or 0,
        new_users_month=new_month or 0,
        total_lessons=total_lessons,
        total_messages=total_messages,
        avg_lessons_per_user=round(avg_lessons, 2),
        avg_streak_days=round(float(avg_streak), 2)
    )


@router.get("/users", response_model=list[UserActivity])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(False),
    sort_by: str = Query("last_activity", regex="^(last_activity|registered_at|total_lessons|streak_days)$"),
    order: str = Query("desc", regex="^(asc|desc)$")
):
    """Get list of all users with their activity status."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    query = select(Student)
    
    if active_only:
        query = query.where(Student.last_activity >= week_ago)
    
    # Dynamic sorting
    sort_column = getattr(Student, sort_by)
    if order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullsfirst())
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    students = result.scalars().all()
    
    users = []
    for student in students:
        days_inactive = 0
        if student.last_activity:
            days_inactive = (now - student.last_activity).days
        
        users.append(UserActivity(
            user_id=student.id,
            telegram_id=student.telegram_id,
            name=student.full_name,
            username=student.username,
            level=student.current_level.code if student.current_level else "PRE_A1",
            total_lessons=student.total_lessons,
            streak_days=student.streak_days,
            last_activity=student.last_activity,
            registered_at=student.registered_at,
            is_active=days_inactive <= 7,
            days_since_last_activity=days_inactive
        ))
    
    return users


@router.get("/users/churned", response_model=list[ChurnedUser])
async def get_churned_users(
    db: AsyncSession = Depends(get_db),
    days_inactive: int = Query(14, ge=7, le=90)
):
    """Get users who stopped using the app (churned)."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days_inactive)
    
    result = await db.execute(
        select(Student)
        .where(Student.last_activity < cutoff)
        .order_by(Student.last_activity.desc())
    )
    students = result.scalars().all()
    
    churned = []
    for student in students:
        days = (now - student.last_activity).days if student.last_activity else 999
        churned.append(ChurnedUser(
            user_id=student.id,
            telegram_id=student.telegram_id,
            name=student.full_name,
            last_activity=student.last_activity,
            days_inactive=days,
            total_lessons=student.total_lessons,
            level=student.current_level.code if student.current_level else "PRE_A1"
        ))
    
    return churned


@router.get("/usage-by-level", response_model=list[UsageByLevel])
async def get_usage_by_level(db: AsyncSession = Depends(get_db)):
    """Get user distribution by level."""
    from app.models import Level
    
    result = await db.execute(
        select(Level.code, func.count(Student.id))
        .join(Student, Student.current_level_id == Level.id)
        .group_by(Level.code, Level.order)
        .order_by(Level.order)
    )
    rows = result.all()
    
    total = sum(count for _, count in rows)
    
    return [
        UsageByLevel(
            level=level,
            user_count=count,
            percentage=round((count / total * 100) if total > 0 else 0, 1)
        )
        for level, count in rows
    ]


@router.get("/daily-stats", response_model=list[DailyStats])
async def get_daily_stats(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=7, le=90)
):
    """Get daily statistics for the last N days."""
    now = datetime.now(timezone.utc)
    stats = []
    
    for i in range(days):
        date = now - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        new_users = await db.scalar(
            select(func.count(Student.id))
            .where(and_(
                Student.registered_at >= day_start,
                Student.registered_at < day_end
            ))
        ) or 0
        
        active_users = await db.scalar(
            select(func.count(Student.id))
            .where(and_(
                Student.last_activity >= day_start,
                Student.last_activity < day_end
            ))
        ) or 0
        
        lessons = await db.scalar(
            select(func.count(Lesson.id))
            .where(and_(
                Lesson.started_at >= day_start,
                Lesson.started_at < day_end
            ))
        ) or 0
        
        messages = await db.scalar(
            select(func.count(LessonMessage.id))
            .where(and_(
                LessonMessage.timestamp >= day_start,
                LessonMessage.timestamp < day_end
            ))
        ) or 0
        
        stats.append(DailyStats(
            date=day_start.strftime("%Y-%m-%d"),
            new_users=new_users,
            active_users=active_users,
            lessons_count=lessons,
            messages_count=messages
        ))
    
    return list(reversed(stats))


@router.get("/token-usage", response_model=list[TokenUsage])
async def get_token_usage(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200)
):
    """Estimate token usage and cost per user."""
    # Estimate: avg 4 chars per token, $0.002 per 1K tokens (GPT-3.5)
    CHARS_PER_TOKEN = 4
    COST_PER_1K_TOKENS = 0.002
    
    result = await db.execute(
        select(
            Student.id,
            Student.first_name,
            Student.last_name,
            func.count(LessonMessage.id).label("msg_count"),
            func.sum(func.length(LessonMessage.content)).label("total_chars")
        )
        .join(Lesson, Lesson.student_id == Student.id)
        .join(LessonMessage, LessonMessage.lesson_id == Lesson.id)
        .group_by(Student.id, Student.first_name, Student.last_name)
        .order_by(func.sum(func.length(LessonMessage.content)).desc())
        .limit(limit)
    )
    rows = result.all()
    
    usage = []
    for row in rows:
        total_chars = row.total_chars or 0
        estimated_tokens = total_chars // CHARS_PER_TOKEN
        estimated_cost = (estimated_tokens / 1000) * COST_PER_1K_TOKENS
        
        name = row.first_name
        if row.last_name:
            name += f" {row.last_name}"
        
        usage.append(TokenUsage(
            user_id=row.id,
            name=name,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=round(estimated_cost, 4),
            messages_count=row.msg_count
        ))
    
    return usage


@router.get("/engagement", response_model=EngagementStats)
async def get_engagement_stats(db: AsyncSession = Depends(get_db)):
    """Get engagement and retention statistics."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    two_weeks_ago = now - timedelta(days=14)
    
    # Users registered more than 7 days ago
    users_7d_ago = await db.scalar(
        select(func.count(Student.id))
        .where(Student.registered_at <= week_ago)
    ) or 1
    
    # Of those, how many were active in last 7 days
    retained_7d = await db.scalar(
        select(func.count(Student.id))
        .where(and_(
            Student.registered_at <= week_ago,
            Student.last_activity >= week_ago
        ))
    ) or 0
    
    # Users registered more than 30 days ago
    users_30d_ago = await db.scalar(
        select(func.count(Student.id))
        .where(Student.registered_at <= month_ago)
    ) or 1
    
    # Of those, how many were active in last 30 days
    retained_30d = await db.scalar(
        select(func.count(Student.id))
        .where(and_(
            Student.registered_at <= month_ago,
            Student.last_activity >= month_ago
        ))
    ) or 0
    
    # Churn: users inactive > 14 days
    total_users = await db.scalar(select(func.count(Student.id))) or 1
    churned = await db.scalar(
        select(func.count(Student.id))
        .where(Student.last_activity < two_weeks_ago)
    ) or 0
    
    # Avg messages per lesson
    avg_msgs = await db.scalar(
        select(func.avg(
            select(func.count(LessonMessage.id))
            .where(LessonMessage.lesson_id == Lesson.id)
            .correlate(Lesson)
            .scalar_subquery()
        ))
    ) or 0
    
    return EngagementStats(
        avg_session_duration_minutes=15.0,  # Placeholder - would need session tracking
        avg_messages_per_session=float(avg_msgs) if avg_msgs else 5.0,
        avg_daily_usage_minutes=10.0,  # Placeholder
        retention_rate_7d=round((retained_7d / users_7d_ago) * 100, 1),
        retention_rate_30d=round((retained_30d / users_30d_ago) * 100, 1),
        churn_rate=round((churned / total_users) * 100, 1)
    )


@router.get("/user/{user_id}")
async def get_user_detail(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed info for a specific user."""
    result = await db.execute(
        select(Student).where(Student.id == user_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get lesson history
    lessons_result = await db.execute(
        select(Lesson)
        .where(Lesson.student_id == user_id)
        .order_by(Lesson.started_at.desc())
        .limit(20)
    )
    lessons = lessons_result.scalars().all()
    
    now = datetime.now(timezone.utc)
    days_inactive = (now - student.last_activity).days if student.last_activity else 999
    
    return {
        "user_id": student.id,
        "telegram_id": student.telegram_id,
        "name": student.full_name,
        "username": student.username,
        "level": student.current_level.code if student.current_level else "PRE_A1",
        "total_lessons": student.total_lessons,
        "total_minutes": student.total_minutes,
        "streak_days": student.streak_days,
        "last_activity": student.last_activity,
        "registered_at": student.registered_at,
        "is_active": days_inactive <= 7,
        "days_since_last_activity": days_inactive,
        "recent_lessons": [
            {
                "id": l.id,
                "started_at": l.started_at,
                "ended_at": l.ended_at,
                "skill": l.skill.code if l.skill else None,
                "score": l.score
            }
            for l in lessons
        ]
    }
