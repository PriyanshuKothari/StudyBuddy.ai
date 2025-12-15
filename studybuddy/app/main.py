"""
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import chat, upload, rag_chat, pyq
from app.middleware.security import RateLimitMiddleware

settings = get_settings()

#Create FastAPI app 
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered study assistant",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware
app.add_middleware(RateLimitMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(rag_chat.router)
app.include_router(pyq.router)

# Root endpoints
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "running",
        "features": ["RAG Chat", "PDF Upload", "Conversation Memory", "PYQ Analysis"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "debug_mode": settings.DEBUG
    }