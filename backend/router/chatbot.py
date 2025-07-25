"""
Chatbot Router for AI-powered travel assistance
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chatbot", tags=["chatbot"])

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    suggestions: Optional[list] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(chat_message: ChatMessage):
    """
    Chat with the travel planning bot
    """
    try:
        # For now, return a simple response
        # In the future, integrate with your AI chatbot logic
        response = f"I received your message: '{chat_message.message}'. How can I help you plan your Sri Lanka trip?"
        
        return ChatResponse(
            response=response,
            session_id=chat_message.session_id or "default-session",
            suggestions=[
                "Plan a 3-day itinerary",
                "Show me beaches in Sri Lanka",
                "Find cultural attractions",
                "Plan a budget trip"
            ]
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def chatbot_health():
    """Health check for chatbot service"""
    return {"status": "healthy", "service": "chatbot"}
