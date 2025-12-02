# app/services/rag_service.py
"""
RAG Service - combines retrieval and generation
"""
from typing import Dict
from app.services.vector_service import query_vector_store
from app.services.llm_service import get_llm

async def answer_with_rag(file_id: str, question: str) -> Dict:
    """
    Answer question using RAG (Retrieval Augmented Generation)
    
    Args:
        file_id: Document to search
        question: User's question
        
    Returns:
        Dictionary with answer and sources
    """
    try:
        # Step 1: Retrieve relevant chunks from vector store
        relevant_chunks = await query_vector_store(file_id, question, k=3)
        
        if not relevant_chunks:
             return {
                "answer": "I couldn't find relevant information in the document to answer this question.",
                "sources": [],
                "context_used": 0
            }
        
        # Step 2: Build context from retrieved chunks
        context= "\n\n".join([
            f"[Chunk {chunk['metadata']['chunk']}]: {chunk['content']}"
            for chunk in relevant_chunks
        ])
        
        # Step 3: Create prompt with context
        prompt = f"""You are StudyBuddy, an AI tutor helping students understand their study materials.

        Use the following context from the student's document to answer their question. If the answer is not in the context, say so.

        CONTEXT:
        {context}

        QUESTION: {question}

        ANSWER (be clear, concise, and helpful):"""
        
        # Step 4: Get answer from LLM
        llm = get_llm()
        response = llm.invoke(prompt)
        answer = response.content
        
        # Step 5: Return answer with sources
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
        