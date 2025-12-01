"""
Chat endpoint - handles user questions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.llm_service import get_ai_response


router= APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"]
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: str = Field(...)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is machine learning?",
                "session_id": "test_session_001"
            }
        }
        
class ChatResponse(BaseModel):
    success: bool
    answer: str
    session_id: str
    metadata: Optional[dict] = None
    
# Chat endpoint
@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - answer user questions using AI
    Now connected to Groq LLM!
    """
    try:
        # Get AI response
        ai_answer = await get_ai_response(request.message)
        
        return ChatResponse(
            success=True,
            answer=ai_answer,
            session_id=request.session_id,
            metadata={
                "status": "ai_powered",
                "model": "llama-3.1-8b-instant"
            }
        )
    
    except ValueError as e:
        # API key missing
        raise HTTPException(
            status_code=500,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )