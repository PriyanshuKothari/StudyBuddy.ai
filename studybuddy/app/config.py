# """
# Configuration management for StudyBuddy.ai
# This file loads settings from .env and makes them available throughout the app
# """

# from pydantic_setting import BaseSettings
# from functools import lru_cache

# class Settings(BaseSettings):
#     """
#     Settings class - reads from .env file automatically
#     WHY: Centralized config means changing API keys doesn't require code changes
#     """
    
#     #API Keys (loaded from .env)
#     GROQ_API_KEY: str  # Must be in .env or app will crash
#     HF_TOKEN: str
    
#      # App Metadata
#     APP_NAME: str = "StudyBuddy.ai"  # Default value
#     VERSION: str = "1.0.0"
#     DEBUG: bool = True  # Set to False in production
    
#     # LLM Configuration
#     LLM_MODEL: str = "llama-3.1-8b-instant"  # Groq model name
#     EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # HuggingFace model
#     TEMPERATURE: float = 0.7  # How "creative" the LLM is (0-1)
#     MAX_TOKENS: int = 1000  # Max response length
    
#     # File Upload Settings
#     MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
#     UPLOAD_DIR: str = "./uploads"  # Where PDFs are stored temporarily
    
#     class Config:
#         """
#         Pydantic config - tells it to read from .env file
#         """
#         env_file = ".env"
#         case_sensitive = True  # GROQ_API_KEY must match exactly


# @lru_cache()  # Cache this function - only create Settings object ONCE
# def get_settings() -> Settings:
#     """
#     Factory function to get settings
#     WHY: Using a function allows FastAPI dependency injection
#     """
#     return Settings()

# app/config.py
try:
    # Preferred import for pydantic v2 (pydantic-settings package)
    from pydantic_settings import BaseSettings  # type: ignore
except Exception:
    # Fallback for environments with pydantic v1
    try:
        from pydantic import BaseSettings  # type: ignore
    except Exception as e:
        raise ImportError(
            "pydantic settings not found. Install 'pydantic-settings' (for pydantic v2) or 'pydantic' (v1)."
        ) from e
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys - Optional for now (we'll add real ones later)
    GROQ_API_KEY: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    
    # App Config
    APP_NAME: str = "StudyBuddy.ai"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" 

@lru_cache()
def get_settings() -> Settings:
    return Settings()

if __name__ == "__main__":
    settings = get_settings()
    print(f"✅ Config loaded successfully!")
    print(f"App: {settings.APP_NAME}")
    print(f"Version: {settings.VERSION}")