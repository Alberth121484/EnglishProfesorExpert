import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import Student, Level, Skill, StudentSkill
from app.models.level import LEVEL_SEED_DATA
from app.models.skill import SKILL_SEED_DATA

logger = logging.getLogger(__name__)


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_student(
        self,
        telegram_id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
        language_code: str = "es"
    ) -> tuple[Student, bool]:
        """Get existing student or create new one. Returns (student, is_new)."""
        
        # Try to find existing student
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.current_level))
            .options(selectinload(Student.skills).selectinload(StudentSkill.skill))
            .options(selectinload(Student.skills).selectinload(StudentSkill.level))
            .where(Student.telegram_id == telegram_id)
        )
        student = result.scalar_one_or_none()
        
        if student:
            # Update last activity and streak
            await self._update_streak(student)
            student.last_activity = datetime.now(timezone.utc)
            await self.db.commit()
            return student, False
        
        # Create new student
        # First, ensure we have the initial level
        level = await self._get_or_create_initial_level()
        
        student = Student(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code=language_code,
            current_level_id=level.id,
            streak_days=1,
            last_streak_date=datetime.now(timezone.utc)
        )
        self.db.add(student)
        await self.db.flush()
        
        # Initialize skills for the student
        await self._initialize_student_skills(student, level)
        
        await self.db.commit()
        await self.db.refresh(student)
        
        # Reload with relationships
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.current_level))
            .options(selectinload(Student.skills).selectinload(StudentSkill.skill))
            .options(selectinload(Student.skills).selectinload(StudentSkill.level))
            .where(Student.id == student.id)
        )
        student = result.scalar_one()
        
        logger.info(f"Created new student: {student.full_name} (telegram_id: {telegram_id})")
        return student, True
    
    async def _get_or_create_initial_level(self) -> Level:
        """Get or create the PRE_A1 level."""
        result = await self.db.execute(
            select(Level).where(Level.code == "PRE_A1")
        )
        level = result.scalar_one_or_none()
        
        if not level:
            # Seed all levels
            await self._seed_levels()
            result = await self.db.execute(
                select(Level).where(Level.code == "PRE_A1")
            )
            level = result.scalar_one()
        
        return level
    
    async def _seed_levels(self):
        """Seed the levels table."""
        for level_data in LEVEL_SEED_DATA:
            result = await self.db.execute(
                select(Level).where(Level.code == level_data["code"])
            )
            if not result.scalar_one_or_none():
                level = Level(**level_data)
                self.db.add(level)
        await self.db.flush()
        logger.info("Seeded levels table")
    
    async def _seed_skills(self):
        """Seed the skills table."""
        for skill_data in SKILL_SEED_DATA:
            result = await self.db.execute(
                select(Skill).where(Skill.code == skill_data["code"])
            )
            if not result.scalar_one_or_none():
                skill = Skill(**skill_data)
                self.db.add(skill)
        await self.db.flush()
        logger.info("Seeded skills table")
    
    async def _initialize_student_skills(self, student: Student, level: Level):
        """Initialize skill tracking for a new student."""
        # Ensure skills exist
        result = await self.db.execute(select(Skill))
        skills = result.scalars().all()
        
        if not skills:
            await self._seed_skills()
            result = await self.db.execute(select(Skill))
            skills = result.scalars().all()
        
        for skill in skills:
            student_skill = StudentSkill(
                student_id=student.id,
                skill_id=skill.id,
                level_id=level.id,
                score=0,
                lessons_completed=0
            )
            self.db.add(student_skill)
        
        await self.db.flush()
    
    async def _update_streak(self, student: Student):
        """Update the student's streak."""
        now = datetime.now(timezone.utc)
        
        if student.last_streak_date:
            days_diff = (now.date() - student.last_streak_date.date()).days
            
            if days_diff == 0:
                # Same day, no update needed
                pass
            elif days_diff == 1:
                # Consecutive day, increase streak
                student.streak_days += 1
                student.last_streak_date = now
            else:
                # Streak broken, reset
                student.streak_days = 1
                student.last_streak_date = now
        else:
            student.streak_days = 1
            student.last_streak_date = now
    
    async def get_student_by_telegram_id(self, telegram_id: int) -> Student | None:
        """Get student by Telegram ID."""
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.current_level))
            .options(selectinload(Student.skills).selectinload(StudentSkill.skill))
            .options(selectinload(Student.skills).selectinload(StudentSkill.level))
            .where(Student.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_student_by_id(self, student_id: int) -> Student | None:
        """Get student by ID."""
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.current_level))
            .options(selectinload(Student.skills).selectinload(StudentSkill.skill))
            .options(selectinload(Student.skills).selectinload(StudentSkill.level))
            .where(Student.id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def update_student_progress(
        self,
        student: Student,
        skills_practiced: list[str] | None = None,
        lesson_duration: int = 0
    ):
        """Update student progress after a lesson interaction."""
        student.total_lessons += 1
        student.total_minutes += lesson_duration
        
        if skills_practiced:
            for skill_code in skills_practiced:
                # Find the student skill
                for student_skill in student.skills:
                    if student_skill.skill.code == skill_code:
                        student_skill.lessons_completed += 1
                        student_skill.last_practiced = datetime.now(timezone.utc)
                        # Increase score slightly (max 100)
                        student_skill.score = min(100, student_skill.score + 2)
                        break
        
        await self.db.commit()
    
    async def update_skill_scores(self, student: Student, evaluation: dict):
        """Update skill scores based on AI evaluation."""
        score_mapping = {
            "VOCABULARY": evaluation.get("vocabulary_score"),
            "GRAMMAR": evaluation.get("grammar_score"),
            "SPEAKING": evaluation.get("fluency_score"),
            "LISTENING": evaluation.get("comprehension_score")
        }
        
        for skill_code, score in score_mapping.items():
            if score is not None:
                for student_skill in student.skills:
                    if student_skill.skill.code == skill_code:
                        # Weighted average with existing score
                        student_skill.score = int(
                            (student_skill.score * 0.7) + (score * 0.3)
                        )
                        break
        
        await self.db.commit()
    
    async def check_level_up(self, student: Student) -> Level | None:
        """Check if student should level up. Returns new level if promoted."""
        # Calculate average score across skills
        if not student.skills:
            return None
        
        avg_score = sum(s.score for s in student.skills) / len(student.skills)
        
        # Need average score >= 75 and at least 10 lessons at current level
        lessons_at_level = sum(
            s.lessons_completed for s in student.skills 
            if s.level_id == student.current_level_id
        ) // len(student.skills)
        
        if avg_score >= 75 and lessons_at_level >= 10:
            # Get next level
            result = await self.db.execute(
                select(Level)
                .where(Level.order == student.current_level.order + 1)
            )
            next_level = result.scalar_one_or_none()
            
            if next_level:
                student.current_level_id = next_level.id
                # Update all skills to new level
                for skill in student.skills:
                    skill.level_id = next_level.id
                    skill.score = max(0, skill.score - 20)  # Reset scores a bit
                
                await self.db.commit()
                logger.info(f"Student {student.full_name} leveled up to {next_level.name}")
                return next_level
        
        return None
    
    async def get_all_levels(self) -> list[Level]:
        """Get all levels ordered."""
        result = await self.db.execute(
            select(Level).order_by(Level.order)
        )
        return list(result.scalars().all())
    
    async def get_next_level(self, current_level: Level) -> Level | None:
        """Get the next level after current."""
        result = await self.db.execute(
            select(Level).where(Level.order == current_level.order + 1)
        )
        return result.scalar_one_or_none()
