import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import StudentResponse, StudentDashboard, SkillProgress
from app.schemas.student import LevelResponse, SkillResponse
from app.services import StudentService, LessonService
from app.api.auth import get_current_student_id

logger = logging.getLogger(__name__)
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
    logger.info(f"Loading dashboard for student_id: {student_id}")
    
    student_service = StudentService(db)
    lesson_service = LessonService(db)
    
    try:
        student = await student_service.get_student_by_id(student_id)
        if not student:
            logger.error(f"Student not found: {student_id}")
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Ensure student has skills initialized
        if not student.skills:
            logger.info(f"Initializing skills for student {student_id}")
            try:
                await student_service.ensure_student_skills(student)
                await db.commit()
                student = await student_service.get_student_by_id(student_id)
            except Exception as e:
                logger.warning(f"Could not initialize skills: {e}")
        
        # Default level for fallback
        default_level = LevelResponse(
            id=1, code="PRE_A1", name="Pre A1 - Principiante",
            description="Nivel inicial para principiantes absolutos", order=1
        )
        
        # Get current level safely
        if student.current_level:
            current_level_response = LevelResponse(
                id=student.current_level.id,
                code=student.current_level.code,
                name=student.current_level.name,
                description=student.current_level.description or "",
                order=student.current_level.order
            )
        else:
            current_level_response = default_level
        
        # Build skills progress with defaults
        skills_progress = []
        default_skills = [
            {"code": "SPEAKING", "name": "Speaking", "icon": "mic"},
            {"code": "LISTENING", "name": "Listening", "icon": "headphones"},
            {"code": "READING", "name": "Reading", "icon": "book-open"},
            {"code": "WRITING", "name": "Writing", "icon": "pencil"},
            {"code": "VOCABULARY", "name": "Vocabulary", "icon": "library"},
            {"code": "GRAMMAR", "name": "Grammar", "icon": "brackets"},
        ]
        
        if student.skills:
            for student_skill in student.skills:
                try:
                    skill_level = LevelResponse(
                        id=student_skill.level.id if student_skill.level else 1,
                        code=student_skill.level.code if student_skill.level else "PRE_A1",
                        name=student_skill.level.name if student_skill.level else "Pre A1",
                        description=student_skill.level.description if student_skill.level else "",
                        order=student_skill.level.order if student_skill.level else 1
                    )
                    skills_progress.append(SkillProgress(
                        skill=SkillResponse(
                            id=student_skill.skill.id if student_skill.skill else 1,
                            code=student_skill.skill.code if student_skill.skill else "UNKNOWN",
                            name=student_skill.skill.name if student_skill.skill else "Unknown",
                            icon=student_skill.skill.icon if student_skill.skill else "help"
                        ),
                        level=skill_level,
                        score=student_skill.score or 0,
                        lessons_completed=student_skill.lessons_completed or 0,
                        last_practiced=student_skill.last_practiced
                    ))
                except Exception as e:
                    logger.warning(f"Error processing skill: {e}")
        
        # If no skills loaded, use defaults with zero values
        if not skills_progress:
            for i, skill_data in enumerate(default_skills):
                skills_progress.append(SkillProgress(
                    skill=SkillResponse(
                        id=i + 1,
                        code=skill_data["code"],
                        name=skill_data["name"],
                        icon=skill_data["icon"]
                    ),
                    level=current_level_response,
                    score=0,
                    lessons_completed=0,
                    last_practiced=None
                ))
        
        # Get recent lessons count safely
        try:
            recent_lessons = await lesson_service.get_recent_lessons_count(student_id, days=7)
        except Exception as e:
            logger.warning(f"Error getting recent lessons: {e}")
            recent_lessons = 0
        
        # Get next level safely
        try:
            next_level = await student_service.get_next_level(student.current_level) if student.current_level else None
        except Exception as e:
            logger.warning(f"Error getting next level: {e}")
            next_level = None
        
        # Calculate level progress safely
        try:
            avg_score = sum(sp.score for sp in skills_progress) / len(skills_progress) if skills_progress else 0
            lessons_at_level = await lesson_service.get_total_lessons_at_level(
                student_id, student.current_level_id or 1
            )
        except Exception as e:
            logger.warning(f"Error calculating progress: {e}")
            avg_score = 0
            lessons_at_level = 0
        
        score_progress = min(100, (avg_score / 75) * 100) if avg_score > 0 else 0
        lesson_progress = min(100, (lessons_at_level / 10) * 100) if lessons_at_level > 0 else 0
        level_progress = int((score_progress * 0.7) + (lesson_progress * 0.3))
        
        # Generate recommendations safely
        try:
            recommendations = generate_recommendations_safe(student, skills_progress, avg_score)
        except Exception as e:
            logger.warning(f"Error generating recommendations: {e}")
            recommendations = ["¡Bienvenido! Comienza a practicar con el bot de Telegram para ver tu progreso."]
        
        return StudentDashboard(
            student=student,
            skills_progress=skills_progress,
            recent_lessons_count=recent_lessons,
            next_level=next_level,
            level_progress_percent=level_progress,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")


@router.get("/levels", response_model=list[LevelResponse])
async def get_all_levels(
    db: AsyncSession = Depends(get_db)
):
    """Get all available levels."""
    student_service = StudentService(db)
    levels = await student_service.get_all_levels()
    return levels


def generate_recommendations_safe(student, skills_progress, avg_score) -> list[str]:
    """Generate personalized recommendations with safe defaults."""
    recommendations = []
    
    # Default recommendation for new users
    if not skills_progress or avg_score == 0:
        recommendations.append("👋 ¡Bienvenido! Envía un mensaje al bot de Telegram para comenzar tu primera lección.")
        recommendations.append("📱 Puedes enviar mensajes de texto o notas de voz para practicar.")
        recommendations.append("🎯 Tu progreso se actualizará automáticamente conforme practiques.")
        return recommendations
    
    # Find weakest skill
    try:
        if skills_progress:
            weakest = min(skills_progress, key=lambda x: x.score)
            if weakest.score < 50:
                recommendations.append(
                    f"💪 Enfócate en mejorar tu {weakest.skill.name}. Practica más ejercicios de esta habilidad."
                )
    except Exception:
        pass
    
    # Check streak
    try:
        streak_days = getattr(student, 'streak_days', 0) or 0
        if streak_days < 3:
            recommendations.append(
                "🔥 ¡Mantén tu racha! Practica al menos una vez al día para mejores resultados."
            )
        elif streak_days >= 7:
            recommendations.append(
                f"🌟 ¡Excelente! Llevas {streak_days} días seguidos. ¡Sigue así!"
            )
    except Exception:
        pass
    
    # Level-based recommendations
    try:
        level_code = getattr(student.current_level, 'code', 'PRE_A1') if student.current_level else 'PRE_A1'
        if level_code == "PRE_A1":
            recommendations.append(
                "📚 Enfócate en aprender vocabulario básico y saludos. Practica pronunciación con audios."
            )
        elif level_code == "A1":
            recommendations.append(
                "📝 Comienza a formar oraciones simples. Practica: 'I am...', 'You are...'"
            )
        elif level_code in ["A2", "B1"]:
            recommendations.append(
                "🗣️ Es momento de practicar más conversaciones. Intenta enviar más notas de voz."
            )
        elif level_code in ["B2", "C1"]:
            recommendations.append(
                "📖 Lee textos más complejos y practica expresar opiniones sobre temas variados."
            )
    except Exception:
        pass
    
    # Progress to next level
    if avg_score >= 70:
        recommendations.append(
            "🚀 ¡Estás cerca de subir de nivel! Sigue practicando para alcanzar 75% de puntuación."
        )
    
    # Ensure at least one recommendation
    if not recommendations:
        recommendations.append("📱 ¡Sigue practicando con el bot para mejorar tus habilidades!")
    
    return recommendations[:4]
