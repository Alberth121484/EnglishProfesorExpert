from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.lesson import LessonResponse, LessonWithMessages
from app.services import LessonService, StudentService
from app.api.auth import get_current_student_id

router = APIRouter()


@router.get("/", response_model=list[LessonResponse])
async def get_lessons(
    student_id: int = Depends(get_current_student_id),
    limit: int = Query(default=10, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get lessons for the current student."""
    lesson_service = LessonService(db)
    lessons = await lesson_service.get_student_lessons(student_id, limit, offset)
    return lessons


@router.get("/{lesson_id}", response_model=LessonWithMessages)
async def get_lesson_detail(
    lesson_id: int,
    student_id: int = Depends(get_current_student_id),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed lesson with messages."""
    lesson_service = LessonService(db)
    lesson = await lesson_service.get_lesson_with_messages(lesson_id)
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if lesson.student_id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return lesson
