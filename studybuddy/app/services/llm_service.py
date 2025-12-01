"""
LLM Service - handles AI model interactions
"""

from langchain_groq import ChatGroq # type: ignore
from app.config import get_settings
from functools import lru_cache

@lru_cache()
def get_llm():
    """
    Initialize and cache the LLM
    Using lru_cache means we only create this once
    """
    settings = get_settings()
    
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")
    
    llm= ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=1000
    )
    return llm

async def get_ai_response(question: str) -> str:
    """
    Get a response from the AI model
    
    Args:
        question: User's question
        
    Returns:
        AI's response as a string
    """
    
    try:
        llm= get_llm()
        # Create a prompt
        prompt = f"""You are StudyBuddy, a helpful AI tutor. Answer the student's question clearly and concisely. Question: {question} Answer:"""
        # Get response from LLM
        response = llm.invoke(prompt)
        
        # Extract text from response
        answer= response.content
        
        return answer
    except Exception as e:
        raise Exception(f"LLM error: {str(e)}")