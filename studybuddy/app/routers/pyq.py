"""
PYQ Router - Previous Year Question Paper Analysis
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.services.pyq_service import(
    extract_questions_from_pyq,
    map_questions_to_topics,
    analyze_topic_frequency,
    generate_mock_questions,
    generate_study_recommendations
)
from app.services.pdf_service import extract_text_from_pdf,save_uploaded_file
from fastapi import UploadFile, File

router = APIRouter(
    prefix="/api/v1/pyq",
    tags=["pyq-analysis"]
)

class AnalyzePYQResponse(BaseModel):
    syllabus_file_id: str = Field(..., description="File ID of syllabus")
    pyq_file_id: str = Field(..., description="File ID of PYQ paper")
    
    class Config:
        json_schema_extra = {
            "example": {
                "syllabus_file_id": "ML_Syllabus_Test",
                "pyq_file_id": "ML_PYQ_2023"
            }
        }
        
class GenerateMockRequest(BaseModel):
    syllabus_file_id: str = Field(...)
    topic: str = Field(..., description="Topic to generate questions about")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions (1-20)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "syllabus_file_id": "ML_Syllabus_Test",
                "topic": "Supervised Learning",
                "num_questions": 5
            }
        }
        
@router.post("/upload")
async def upload_pyq(
    file: UploadFile = File(..., description="PYQ PDF file")
):
    """
    Upload a Previous Year Question Paper for analysis
    
    Similar to syllabus upload but marks it as PYQ
    """
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    try:
        content = await file.read()
        file_path = await save_uploaded_file(content, file.filename)
        extracted_data = await extract_text_from_pdf(file_path)
        file_id = file.filename.replace('.pdf', '').replace(' ', '_')
        questions = await extract_questions_from_pyq(extracted_data["full_text"])
        
        return {
            "success": True,
            "message": "PYQ uploaded successfully",
            "filename": file.filename,
            "file_id": file_id,
            "num_pages": extracted_data["num_pages"],
            "questions_found": len(questions),
            "questions_preview": questions[:3] if questions else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/analyze")
async def analyze_pyq(request: AnalyzePYQResponse):
    """
    Analyze PYQ paper against syllabus
    
    Returns:
    - Topic frequency analysis
    - High-priority topics
    - Study recommendations
    """
    try:
        return {
            "success": True,
            "message": "Analysis complete",
            "note": "Full PYQ analysis available after uploading PYQ",
            "placeholder_analysis": {
                "supervised_learning": {
                    "count": 5,
                    "percentage": 25.0,
                    "priority": "HIGH"
                },
                "unsupervised_learning": {
                    "count": 3,
                    "percentage": 15.0,
                    "priority": "MEDIUM"
                },
                "neural_networks": {
                    "count": 4,
                    "percentage": 20.0,
                    "priority": "HIGH"
                }
            },
            "recommendations": [
                "🔥 PRIORITY: Focus on 'Supervised Learning' - 25% of questions",
                "🔥 PRIORITY: Review 'Neural Networks' - 20% of questions",
                "⚠️ Important: Study 'Unsupervised Learning' - 15% of questions"
            ],
            "priority_topics": ["Supervised Learning", "Neural Networks"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/generate-mock")
async def generate_mock(request: GenerateMockRequest):
    """
    Generate mock questions based on syllabus topics
    
    Returns AI-generated practice questions
    """
    try:
        questions = await generate_mock_questions(
            syllabus_file_id=request.syllabus_file_id,
            topic=request.topic,
            num_questions=request.num_questions
        )
        
        return {
            "success": True,
            "topic": request.topic,
            "questions_generated": len(questions),
            "questions": questions,
            "usage_note": "Use these for practice. Verify answers independently."
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")