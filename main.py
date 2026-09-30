
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

from chat_history import get_history
from chat_service import get_reply, update_long_term_memory
from logger_config import get_logger
from summarizer_memory import create_and_save_summary


logger = get_logger("main")
app = FastAPI()


class ChatRequest(BaseModel):
    """Request model for sending a chat message."""

    user_id: str
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response model containing the assistant reply."""

    reply: str


class EndSessionRequest(BaseModel):
    """Request model for ending a chat session."""

    user_id: str
    session_id: str


@app.post("/end_session")
def end_session_endpoint(req: EndSessionRequest):
    """End a chat session and save a summary of the conversation.

    Args:
        req: Request containing the user ID and session ID.

    Returns:
        A status message indicating that the session summary was saved.
    """
    rows = get_history(req.user_id, req.session_id, limit=50)

    if rows:
        conversation = [
            (role, message)
            for role, message, _ in rows
        ]

        create_and_save_summary(
            req.user_id,
            req.session_id,
            conversation,
        )

    return {"status": "session summary saved"}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
) -> ChatResponse:
    """Process a chat message and update long-term memory in the background.

    Args:
        req: Request containing the user ID, session ID, and message.
        background_tasks: FastAPI background task manager.

    Returns:
        A ChatResponse containing the assistant reply.

    Raises:
        HTTPException: If processing the chat message fails.
    """
    try:
        ai_text, recent_messages = get_reply(
            req.user_id,
            req.session_id,
            req.message,
        )
    except Exception:
        logger.exception(
            "chat_endpoint failed | user=%s session=%s",
            req.user_id,
            req.session_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again.",
        )

    background_tasks.add_task(
        update_long_term_memory,
        req.user_id,
        req.session_id,
        req.message,
        ai_text,
        recent_messages,
    )

    return ChatResponse(reply=ai_text)
