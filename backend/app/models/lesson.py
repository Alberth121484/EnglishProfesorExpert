from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Lesson(Base):
    __tablename__ = "lessons"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    messages_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    
    # AI Evaluation stored as JSON
    ai_evaluation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Example: {"vocabulary_used": 15, "grammar_errors": 2, "fluency_score": 75, "topics": ["greetings", "numbers"]}
    
    skills_practiced: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # Example: ["SPEAKING", "LISTENING", "VOCABULARY"]
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    student: Mapped["Student"] = relationship(back_populates="lessons")
    level: Mapped["Level"] = relationship(back_populates="lessons")
    messages: Mapped[list["LessonMessage"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
