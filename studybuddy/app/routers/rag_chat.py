# app/routers/rag_chat.py
"""
RAG Chat Router - chat with uploaded PDFs
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from app.services.rag_service import answer_with_rag
from app.services.session_service import (
    add_message,
    get_chat_history,
    clear_chat_history,
    get_session_info
)

router = APIRouter(
    prefix="/api/v1/rag",
    tags=["rag-chat"]
)


class RAGChatRequest(BaseModel):
    file_id: str = Field(..., description="ID of uploaded PDF")
    question: str = Field(..., min_length=1, max_length=500)
    session_id: str = Field(default="default", description="Session ID for conversation history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "ML_Syllabus_Test",
                "question": "What topics are covered in supervised learning?",
                "session_id": "user_123_session"
            }
        }


class RAGChatResponse(BaseModel):
    success: bool
    answer: str
    sources: List[Dict]
    context_used: int
    file_id: str
    session_id: str
    message_count: int


@router.post("/chat", response_model=RAGChatResponse)
async def rag_chat(request: RAGChatRequest):
    """
    Ask questions about uploaded PDFs using RAG with conversation history
    
    - **file_id**: The file_id returned from upload endpoint
    - **question**: Your question about the document
    - **session_id**: Optional session ID (default: "default")
    
    Returns AI answer based on document content with sources.
    Remembers previous questions in the same session!
    """
    try:
        add_message(
            session_id=request.session_id,
            role="user",
            content=request.question,
            metadata={"file_id": request.file_id}
        )
        
        result = await answer_with_rag(
            file_id=request.file_id,
            question=request.question,
            session_id=request.session_id
        )
        
        add_message(
            session_id=request.session_id,
            role="assistant",
            content=result["answer"],
            metadata={
                "file_id": request.file_id,
                "sources": result["sources"],
                "context_used": result["context_used"]
            }
        )
        
        session_info = get_session_info(request.session_id)
        
        return RAGChatResponse(
            success=True,
            answer=result["answer"],
            sources=result["sources"],
            context_used=result["context_used"],
            file_id=request.file_id,
            session_id=request.session_id,
            message_count=session_info["message_count"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404,detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error: {str(e)}")
    
@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """
    Get chat history for a session
    
    Returns all messages in chronological order
    """
    history= get_chat_history(session_id)
    session_info= get_session_info(session_id)
    
    return {
        "session_info": session_info,
        "message" : history
    }

@router.delete("/history/{session_id}")
async def delete_history(session_id: str):
    """
    Clear chat history for a session
    
    Useful for starting fresh or privacy
    """
    success= clear_chat_history(session_id)
    
    if success:
        return {"success": True, "message": f"Cleared history for session {session_id}"}
    else:
        return {"success": False, "message": f"No history found for session {session_id}"}