from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentDashboard,
    SkillProgress
)
from app.schemas.lesson import (
    LessonCreate,
    LessonResponse,
    LessonMessageCreate,
    LessonMessageResponse
)
from app.schemas.auth import TelegramAuthData, TokenResponse

__all__ = [
    "StudentCreate",
    "StudentUpdate", 
    "StudentResponse",
    "StudentDashboard",
    "SkillProgress",
    "LessonCreate",
    "LessonResponse",
    "LessonMessageCreate",
    "LessonMessageResponse",
    "TelegramAuthData",
    "TokenResponse"
]
