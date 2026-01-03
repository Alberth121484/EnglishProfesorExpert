from datetime import datetime
from pydantic import BaseModel


class LessonMessageCreate(BaseModel):
    role: str
    content: str
    audio_file_id: str | None = None


class LessonMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    audio_file_id: str | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LessonCreate(BaseModel):
    student_id: int
    level_id: int
    topic: str | None = None


class LessonUpdate(BaseModel):
    topic: str | None = None
    summary: str | None = None
    ai_evaluation: dict | None = None
    skills_practiced: list[str] | None = None
    ended_at: datetime | None = None


class LessonResponse(BaseModel):
    id: int
    student_id: int
    topic: str | None = None
    summary: str | None = None
    messages_count: int
    duration_minutes: int
    ai_evaluation: dict | None = None
    skills_practiced: list[str] | None = None
    started_at: datetime
    ended_at: datetime | None = None
    
    class Config:
        from_attributes = True


class LessonWithMessages(LessonResponse):
    messages: list[LessonMessageResponse] = []
