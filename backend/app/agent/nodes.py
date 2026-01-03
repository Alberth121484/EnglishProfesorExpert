import json
import logging
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.config import get_settings
from app.agent.state import TutorState
from app.agent.prompts import SYSTEM_PROMPT, EVALUATION_PROMPT

settings = get_settings()
logger = logging.getLogger(__name__)

llm = ChatOpenAI(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
    temperature=0.7
)

evaluation_llm = ChatOpenAI(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
    temperature=0.3
)


def build_system_message(state: TutorState) -> SystemMessage:
    """Build the system message with student context."""
    prompt = SYSTEM_PROMPT.format(
        student_name=state["student_name"],
        current_level=state["current_level"],
        total_lessons=state["total_lessons"],
        streak_days=state["streak_days"],
        words_learned=state.get("words_learned", 0)
    )
    return SystemMessage(content=prompt)


async def initialize_session(state: TutorState) -> dict:
    """Initialize or continue a session."""
    logger.info(f"Initializing session for student {state['student_id']}")
    
    updates = {
        "session_started": True
    }
    
    # Add system message if this is a new conversation
    if not state.get("messages") or len(state["messages"]) == 0:
        system_msg = build_system_message(state)
        updates["messages"] = [system_msg]
    
    return updates


async def process_input(state: TutorState) -> dict:
    """Process user input and add to messages."""
    user_message = HumanMessage(content=state["user_input"])
    
    return {
        "messages": [user_message]
    }


async def generate_response(state: TutorState) -> dict:
    """Generate tutor response using LLM."""
    logger.info(f"Generating response for student {state['student_id']}")
    
    # Ensure system message is present
    messages = list(state["messages"])
    if not messages or not isinstance(messages[0], SystemMessage):
        system_msg = build_system_message(state)
        messages = [system_msg] + messages
    
    try:
        response = await llm.ainvoke(messages)
        ai_message = AIMessage(content=response.content)
        
        # Determine if we should evaluate (every 5 messages or explicit end)
        message_count = len([m for m in messages if isinstance(m, HumanMessage)])
        should_evaluate = message_count > 0 and message_count % 5 == 0
        
        return {
            "messages": [ai_message],
            "response": response.content,
            "should_evaluate": should_evaluate
        }
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        error_response = "Lo siento, tuve un problema técnico. ¿Puedes repetir lo que dijiste?"
        return {
            "messages": [AIMessage(content=error_response)],
            "response": error_response,
            "should_evaluate": False
        }


async def evaluate_lesson(state: TutorState) -> dict:
    """Evaluate the lesson progress (runs periodically)."""
    if not state.get("should_evaluate", False):
        return {}
    
    logger.info(f"Evaluating lesson for student {state['student_id']}")
    
    # Build conversation summary for evaluation
    messages = state.get("messages", [])
    conversation_text = "\n".join([
        f"{'Usuario' if isinstance(m, HumanMessage) else 'Tutor'}: {m.content}"
        for m in messages
        if isinstance(m, (HumanMessage, AIMessage))
    ][-10:])  # Last 10 messages
    
    eval_prompt = EVALUATION_PROMPT.format(
        conversation=conversation_text,
        level=state["current_level"]
    )
    
    try:
        response = await evaluation_llm.ainvoke([HumanMessage(content=eval_prompt)])
        evaluation = json.loads(response.content)
        logger.info(f"Evaluation complete: {evaluation.get('summary', 'N/A')}")
        # The evaluation will be saved by the service layer
        return {"evaluation": evaluation}
    except Exception as e:
        logger.error(f"Error evaluating lesson: {e}")
        return {}


def route_after_init(state: TutorState) -> str:
    """Route after initialization."""
    return "process_input"


def route_after_response(state: TutorState) -> str:
    """Route after generating response."""
    if state.get("should_evaluate", False):
        return "evaluate"
    return "__end__"
