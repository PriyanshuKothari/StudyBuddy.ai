# app/services/pdf_service.py
"""
PDF Service - handles PDF upload, parsing, and storage
"""
import os
from typing import List, Dict
from pathlib import Path
from pypdf import PdfReader
from app.config import get_settings

settings= get_settings()

async def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Save uploaded PDF file to disk
    
    Args:
        file_content: PDF file bytes
        filename: Original filename
        
    Returns:
        Full path to saved file
    """
    # Create safe filename (remove any path traversal attempts)
    safe_filename = Path(filename).name
    
    # Create full path
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path


async def extract_text_from_pdf(file_path: str) -> Dict[str, any]:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Dictionary with extracted text and metadata
    """
    try:
        reader = PdfReader(file_path)
        
        # Extract text from all pages
        full_text = ""
        page_texts = []
        
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            page_texts.append({
                "page_number": i + 1,
                "text": page_text
            })
            full_text += f"\n\n--- Page {i + 1} ---\n\n{page_text}"
        
        return {
            "success": True,
            "filename": Path(file_path).name,
            "num_pages": len(reader.pages),
            "full_text": full_text,
            "pages": page_texts,
            "file_path": file_path
        }
        
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")
    
async def delete_file(file_path: str) -> bool:
    """
    Delete uploaded file (cleanup)
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Warning: Could not delete file {file_path}: {e}")
        return False