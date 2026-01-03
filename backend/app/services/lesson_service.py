import logging
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Lesson, LessonMessage, Student

logger = logging.getLogger(__name__)


class LessonService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_active_lesson(self, student: Student) -> Lesson:
        """Get active lesson or create a new one."""
        # Check for active lesson (started today, not ended)
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        result = await self.db.execute(
            select(Lesson)
            .where(
                Lesson.student_id == student.id,
                Lesson.ended_at.is_(None),
                Lesson.started_at >= today_start
            )
            .order_by(Lesson.started_at.desc())
        )
        lesson = result.scalar_one_or_none()
        
        if lesson:
            return lesson
        
        # Create new lesson
        lesson = Lesson(
            student_id=student.id,
            level_id=student.current_level_id
        )
        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)
        
        logger.info(f"Created new lesson {lesson.id} for student {student.id}")
        return lesson
    
    async def add_message(
        self,
        lesson: Lesson,
        role: str,
        content: str,
        audio_file_id: str | None = None
    ) -> LessonMessage:
        """Add a message to the lesson."""
        message = LessonMessage(
            lesson_id=lesson.id,
            role=role,
            content=content,
            audio_file_id=audio_file_id
        )
        self.db.add(message)
        
        # Update lesson message count
        lesson.messages_count += 1
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def update_lesson_evaluation(
        self,
        lesson: Lesson,
        evaluation: dict
    ):
        """Update lesson with AI evaluation."""
        lesson.ai_evaluation = evaluation
        lesson.summary = evaluation.get("summary")
        lesson.skills_practiced = evaluation.get("skills_practiced", [])
        lesson.topic = ", ".join(evaluation.get("topics_covered", [])[:3])
        
        await self.db.commit()
    
    async def end_lesson(self, lesson: Lesson):
        """Mark a lesson as ended."""
        lesson.ended_at = datetime.now(timezone.utc)
        
        # Calculate duration
        if lesson.started_at:
            duration = lesson.ended_at - lesson.started_at
            lesson.duration_minutes = int(duration.total_seconds() / 60)
        
        await self.db.commit()
    
    async def get_student_lessons(
        self,
        student_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> list[Lesson]:
        """Get lessons for a student."""
        result = await self.db.execute(
            select(Lesson)
            .where(Lesson.student_id == student_id)
            .order_by(Lesson.started_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_lesson_with_messages(self, lesson_id: int) -> Lesson | None:
        """Get a lesson with all its messages."""
        result = await self.db.execute(
            select(Lesson)
            .options(selectinload(Lesson.messages))
            .where(Lesson.id == lesson_id)
        )
        return result.scalar_one_or_none()
    
    async def get_recent_lessons_count(
        self,
        student_id: int,
        days: int = 7
    ) -> int:
        """Get count of lessons in the last N days."""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            result = await self.db.execute(
                select(func.count(Lesson.id))
                .where(
                    Lesson.student_id == student_id,
                    Lesson.started_at >= cutoff
                )
            )
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def get_total_lessons_at_level(
        self,
        student_id: int,
        level_id: int
    ) -> int:
        """Get total lessons completed at a specific level."""
        result = await self.db.execute(
            select(func.count(Lesson.id))
            .where(
                Lesson.student_id == student_id,
                Lesson.level_id == level_id,
                Lesson.ended_at.isnot(None)
            )
        )
        return result.scalar() or 0
