from datetime import datetime
from pydantic import BaseModel


class LevelResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    order: int
    
    class Config:
        from_attributes = True


class SkillResponse(BaseModel):
    id: int
    code: str
    name: str
    icon: str | None = None
    
    class Config:
        from_attributes = True


class SkillProgress(BaseModel):
    skill: SkillResponse
    level: LevelResponse
    score: int
    lessons_completed: int
    last_practiced: datetime | None = None
    
    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str = "es"


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    current_level_id: int | None = None


class StudentResponse(BaseModel):
    id: int
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    current_level: LevelResponse
    total_lessons: int
    total_minutes: int
    streak_days: int
    registered_at: datetime
    last_activity: datetime
    
    class Config:
        from_attributes = True


class StudentDashboard(BaseModel):
    student: StudentResponse
    skills_progress: list[SkillProgress]
    recent_lessons_count: int
    next_level: LevelResponse | None = None
    level_progress_percent: int  # 0-100 progress to next level
    recommendations: list[str]
