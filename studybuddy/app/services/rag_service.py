# app/services/rag_service.py
"""
RAG Service - combines retrieval and generation
"""
from typing import Dict, Optional
from app.services.vector_service import query_vector_store
from app.services.llm_service import get_llm
from app.services.session_service import get_conversation_context
from app.services.pinecone_vector_service import query_vector_store_pinecone

async def answer_with_rag(file_id: str, question: str, session_id: Optional[str] = None) -> Dict:
    """
    Answer question using RAG (Retrieval Augmented Generation)

    Args:
        file_id: Document to search
        question: User's question   
        
    Returns:
        Dictionary with answer and sources
    """
    try:
        # Step 1: Get conversation history if session_id provided
        conversation_context=""
        if session_id:
            conversation_context = get_conversation_context(session_id, max_messages=4)
        
        
        # Step 2: Retrieve relevant chunks from vector store
        relevant_chunks = await query_vector_store_pinecone(file_id, question, k=3)
        
        if not relevant_chunks:
             return {
                "answer": "I couldn't find relevant information in the document to answer this question.",
                "sources": [],
                "context_used": 0
            }
        
        # Step 3: Build context from retrieved chunks
        context= "\n\n".join([
            f"[Chunk {chunk['metadata']['chunk']}]: {chunk['content']}"
            for chunk in relevant_chunks
        ])
        
        # Step 4: Create prompt with context
        prompt_parts = ["You are StudyBuddy, an AI tutor helping students understand their study materials."]
        
        # Add conversation history if available
        if conversation_context:
            prompt_parts.append(f"\nPREVIOUS CONVERSATION:\n{conversation_context}\n")
        
        prompt_parts.append(f"""
        Use the following context from the student's document to answer their question. 
        If they're asking a follow-up question, consider the previous conversation.
        If the answer is not in the context, say so.

        DOCUMENT CONTEXT:
        {context}

        CURRENT QUESTION: {question}

        ANSWER (be clear, concise, and helpful):""")
        
        prompt = "\n".join(prompt_parts)
        
        # Step 5: Get answer from LLM
        llm = get_llm()
        response = llm.invoke(prompt)
        answer = response.content
        
        # Step 6: Return answer with sources
        return {
            "answer": answer,
            "sources": [
                {
                    "chunk_id": chunk['metadata']['chunk'],
                    "content_preview": chunk['content'][:200] + "...",
                    "similarity": chunk['similarity_score']
                }
                for chunk in relevant_chunks
            ],
            "context_used": len(relevant_chunks)
        }
    except ValueError as e:
        # No vector store found
        raise ValueError(f"Document not found. Please upload the PDF first. Error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error in RAG: {str(e)}")
        