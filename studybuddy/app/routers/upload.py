# app/routers/upload.py
"""
Upload router - handles PDF file uploads
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.pdf_service import save_uploaded_file, extract_text_from_pdf
from app.config import get_settings

settings = get_settings()

router= APIRouter(
    prefix="/api/v1/upload",
    tags=["upload"]
)

class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    num_pages: int
    text_preview: str # First 500 chars
    file_id: str # For tracking
    
@router.post("/pdf", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload")
):
    """
    Upload a PDF file for processing
    
    - **file**: PDF file (max 10MB)
    
    Returns file info and text preview
    """
    
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE / (1024 * 1024)} MB.")
    
    
    try:
        # Save file
        file_path = await save_uploaded_file(content, file.filename)
        
        # Extract text
        extracted_data = await extract_text_from_pdf(file_path)
        
        # Generate file ID (use filename without extension for now)
        file_id = file.filename.replace('.pdf', '')
        
        return UploadResponse(
            success=True,
            message="PDF uploaded and processed successfully",
            filename=file.filename,
            num_pages=extracted_data["num_pages"],
            text_preview=extracted_data["full_text"][:500] + "...",
            file_id=file_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")