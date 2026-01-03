from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import StudentResponse, StudentDashboard, SkillProgress
from app.schemas.student import LevelResponse, SkillResponse
from app.services import StudentService, LessonService
from app.api.auth import get_current_student_id

router = APIRouter()


@router.get("/me", response_model=StudentResponse)
async def get_current_student(
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated student."""
    student_service = StudentService(db)
    student = await student_service.get_student_by_id(student_id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.get("/me/dashboard", response_model=StudentDashboard)
async def get_student_dashboard(
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Get complete dashboard data for current student."""
    student_service = StudentService(db)
    lesson_service = LessonService(db)
    
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get skills progress
    skills_progress = []
    for student_skill in student.skills:
        skills_progress.append(SkillProgress(
            skill=SkillResponse(
                id=student_skill.skill.id,
                code=student_skill.skill.code,
                name=student_skill.skill.name,
                icon=student_skill.skill.icon
            ),
            level=LevelResponse(
                id=student_skill.level.id,
                code=student_skill.level.code,
                name=student_skill.level.name,
                description=student_skill.level.description,
                order=student_skill.level.order
            ),
            score=student_skill.score,
            lessons_completed=student_skill.lessons_completed,
            last_practiced=student_skill.last_practiced
        ))
    
    # Get recent lessons count
    recent_lessons = await lesson_service.get_recent_lessons_count(student_id, days=7)
    
    # Get next level
    next_level = await student_service.get_next_level(student.current_level)
    
    # Calculate level progress
    avg_score = sum(s.score for s in student.skills) / len(student.skills) if student.skills else 0
    lessons_at_level = await lesson_service.get_total_lessons_at_level(
        student_id, student.current_level_id
    )
    
    # Progress is based on score (70%) and lessons (30%)
    score_progress = min(100, (avg_score / 75) * 100)
    lesson_progress = min(100, (lessons_at_level / 10) * 100)
    level_progress = int((score_progress * 0.7) + (lesson_progress * 0.3))
    
    # Generate recommendations
    recommendations = generate_recommendations(student, skills_progress, avg_score)
    
    return StudentDashboard(
        student=student,
        skills_progress=skills_progress,
        recent_lessons_count=recent_lessons,
        next_level=next_level,
        level_progress_percent=level_progress,
        recommendations=recommendations
    )


@router.get("/levels", response_model=list[LevelResponse])
async def get_all_levels(
    db: AsyncSession = Depends(get_db)
):
    """Get all available levels."""
    student_service = StudentService(db)
    levels = await student_service.get_all_levels()
    return levels


def generate_recommendations(student, skills_progress, avg_score) -> list[str]:
    """Generate personalized recommendations."""
    recommendations = []
    
    # Find weakest skill
    if skills_progress:
        weakest = min(skills_progress, key=lambda x: x.score)
        if weakest.score < 50:
            recommendations.append(
                f"💪 Enfócate en mejorar tu {weakest.skill.name}. Practica más ejercicios de esta habilidad."
            )
    
    # Check streak
    if student.streak_days < 3:
        recommendations.append(
            "🔥 ¡Mantén tu racha! Practica al menos una vez al día para mejores resultados."
        )
    elif student.streak_days >= 7:
        recommendations.append(
            f"🌟 ¡Excelente! Llevas {student.streak_days} días seguidos. ¡Sigue así!"
        )
    
    # Level-based recommendations
    if student.current_level.code == "PRE_A1":
        recommendations.append(
            "📚 Enfócate en aprender vocabulario básico y saludos. Practica pronunciación con audios."
        )
    elif student.current_level.code == "A1":
        recommendations.append(
            "📝 Comienza a formar oraciones simples. Practica: 'I am...', 'You are...'"
        )
    elif student.current_level.code in ["A2", "B1"]:
        recommendations.append(
            "🗣️ Es momento de practicar más conversaciones. Intenta enviar más notas de voz."
        )
    elif student.current_level.code in ["B2", "C1"]:
        recommendations.append(
            "📖 Lee textos más complejos y practica expresar opiniones sobre temas variados."
        )
    
    # Progress to next level
    if avg_score >= 70:
        recommendations.append(
            "🚀 ¡Estás cerca de subir de nivel! Sigue practicando para alcanzar 75% de puntuación."
        )
    
    return recommendations[:4]  # Return max 4 recommendations
