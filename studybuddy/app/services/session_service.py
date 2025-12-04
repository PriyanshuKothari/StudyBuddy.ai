# app/services/session_service.py
"""
Session Service - manages chat history for conversations
"""
from typing import List, Dict
from datetime import datetime

_sessions: Dict[str, List[Dict]] = {}


def get_chat_history(session_id: str) -> List[Dict]:
    """
    Get chat history for a session
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        List of messages in chronological order
    """
    return _sessions.get(session_id, [])

def add_message(session_id: str, role: str, content: str, metadata: Dict = None) -> None:
    """
    Add a message to chat history
    
    Args:
        session_id: Unique session identifier
        role: 'user' or 'assistant'
        content: Message content
        metadata: Optional metadata (sources, file_id, etc.)
    """
    if session_id not in _sessions:
        _sessions[session_id] = []
        
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    _sessions[session_id].append(message)
    
def clear_chat_history(session_id: str) -> bool:
    """
    Clear chat history for a session
    
    Args:
        session_id: Session to clear
        
    Returns:
        True if cleared, False if session didn't exist
    """
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False

def get_conversation_context(session_id: str, max_messages: int = 6) -> str:
    """
    Get recent conversation as formatted context
    
    Args:
        session_id: Session identifier
        max_messages: Maximum recent messages to include
        
    Returns:
        Formatted conversation string for LLM context
    """
    history = get_chat_history(session_id)
    
    if not history:
        return "No conversation history available."
    
    # get the last messages
    recent= history[-max_messages:]
    
    # Format as conversation
    formatted= []
    for msg in recent:
        role = "Student" if msg["role"] == "user" else "StudyBuddy"
        formatted.append(f"{role}: {msg['content']}")
    
    return "\n".join(formatted)

def get_session_info(session_id: str) -> Dict:
    """
    Get session statistics
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with session info
    """
    history = get_chat_history(session_id)
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "user_messages": len([m for m in history if m["role"] == "user"]),
        "assistant_messages": len([m for m in history if m["role"] == "assistant"]),
        "created_at": history[0]["timestamp"] if history else None,
        "last_activity": history[-1]["timestamp"] if history else None
    }