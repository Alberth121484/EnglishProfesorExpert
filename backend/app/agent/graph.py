import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agent.state import TutorState
from app.agent.nodes import (
    initialize_session,
    process_input,
    generate_response,
    evaluate_lesson,
    route_after_response
)
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Global graph instance
_graph = None
_checkpointer = None


def create_tutor_graph() -> StateGraph:
    """Create the tutor conversation graph."""
    
    # Build the graph
    workflow = StateGraph(TutorState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_session)
    workflow.add_node("process_input", process_input)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("evaluate", evaluate_lesson)
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Add edges
    workflow.add_edge("initialize", "process_input")
    workflow.add_edge("process_input", "generate_response")
    
    # Conditional routing after response
    workflow.add_conditional_edges(
        "generate_response",
        route_after_response,
        {
            "evaluate": "evaluate",
            "__end__": END
        }
    )
    
    workflow.add_edge("evaluate", END)
    
    return workflow


async def get_checkpointer():
    """Get or create the PostgreSQL checkpointer."""
    global _checkpointer
    
    if _checkpointer is None:
        # Convert async URL to sync for checkpointer
        db_url = settings.database_url.replace("+asyncpg", "")
        _checkpointer = AsyncPostgresSaver.from_conn_string(db_url)
        await _checkpointer.setup()
    
    return _checkpointer


async def get_compiled_graph():
    """Get the compiled graph with checkpointer."""
    global _graph
    
    if _graph is None:
        workflow = create_tutor_graph()
        checkpointer = await get_checkpointer()
        _graph = workflow.compile(checkpointer=checkpointer)
    
    return _graph


async def get_tutor_response(
    telegram_id: int,
    student_id: int,
    student_name: str,
    current_level: str,
    current_level_id: int,
    total_lessons: int,
    streak_days: int,
    user_input: str,
    lesson_id: int | None = None,
    is_audio: bool = False,
    audio_file_id: str | None = None,
    is_new_student: bool = False
) -> tuple[str, dict | None]:
    """
    Get a response from the tutor agent.
    
    Returns:
        tuple: (response_text, evaluation_dict or None)
    """
    graph = await get_compiled_graph()
    
    # Thread ID based on telegram_id for conversation continuity
    thread_id = f"student_{telegram_id}"
    
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # Initial state
    input_state = {
        "student_id": student_id,
        "telegram_id": telegram_id,
        "student_name": student_name,
        "current_level": current_level,
        "current_level_id": current_level_id,
        "total_lessons": total_lessons,
        "streak_days": streak_days,
        "user_input": user_input,
        "lesson_id": lesson_id,
        "is_audio": is_audio,
        "audio_file_id": audio_file_id,
        "is_new_student": is_new_student,
        "session_started": False,
        "should_evaluate": False,
        "response": ""
    }
    
    try:
        # Run the graph
        result = await graph.ainvoke(input_state, config)
        
        response = result.get("response", "Lo siento, hubo un error. Intenta de nuevo.")
        evaluation = result.get("evaluation")
        
        return response, evaluation
        
    except Exception as e:
        logger.error(f"Error in tutor agent: {e}")
        return "Lo siento, tuve un problema técnico. ¿Puedes intentar de nuevo?", None
