# app/routers/rag_chat.py
"""
RAG Chat Router - chat with uploaded PDFs
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from app.services.rag_service import answer_with_rag

router = APIRouter(
    prefix="/api/v1/rag",
    tags=["rag-chat"]
)


class RAGChatRequest(BaseModel):
    file_id: str = Field(..., description="ID of uploaded PDF")
    question: str = Field(..., min_length=1, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "ML_Syllabus_Test",
                "question": "What topics are covered in supervised learning?"
            }
        }


class RAGChatResponse(BaseModel):
    success: bool
    answer: str
    sources: List[Dict]
    context_used: int
    file_id: str


@router.post("/chat", response_model=RAGChatResponse)
async def rag_chat(request: RAGChatRequest):
    """
    Ask questions about uploaded PDFs using RAG
    
    - **file_id**: The file_id returned from upload endpoint
    - **question**: Your question about the document
    
    Returns AI answer based on document content with sources
    """
    try:
        result = await answer_with_rag(
            file_id=request.file_id,
            question=request.question
        )
        
        return RAGChatResponse(
            success=True,
            answer=result["answer"],
            sources=result["sources"],
            context_used=result["context_used"],
            file_id=request.file_id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )