from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TutorState(TypedDict):
    """State for the English tutor agent."""
    
    # Core conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # Student info
    student_id: int
    telegram_id: int
    student_name: str
    current_level: str
    current_level_id: int
    total_lessons: int
    streak_days: int
    words_learned: int  # Vocabulary words learned
    
    # Session info
    lesson_id: int | None
    session_started: bool
    is_new_student: bool
    
    # Current interaction
    user_input: str
    is_audio: bool
    audio_file_id: str | None
    
    # Response
    response: str
    should_evaluate: bool
    evaluation: dict | None
