# app/config.py
from pydantic import BaseModel
from pydantic_settings import BaseSettings # type: ignore
from functools import lru_cache
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys - Optional for now (we'll add real ones later)
    GROQ_API_KEY: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    
    # App Config
    APP_NAME: str = "StudyBuddy.ai"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    #LLM Config
    LLM_MODEL: str = "llama-3.1-8b-instant"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 500
    
    #PDF Upload Config
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024 # Max file size in MB
    ALLOWED_EXTENSIONS: list = [".pdf"]
    
    #Vector DB Config
    CHROMA_DIR: str = "./chroma_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" 

@lru_cache()
def get_settings() -> Settings:
    
    settings = Settings()
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_DIR, exist_ok=True)
    
    
    return settings

if __name__ == "__main__":
    settings = get_settings()
    print(f"✅ Config loaded successfully!")
    print(f"App: {settings.APP_NAME}")
    print(f"Version: {settings.VERSION}")
    print(f"Upload dir: {settings.UPLOAD_DIR}")
    print(f"Chroma dir: {settings.CHROMA_DIR}")