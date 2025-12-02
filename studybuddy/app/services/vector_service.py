# app/services/vector_service.py
"""
Vector Service - handles embeddings, vector storage, and RAG
"""
from typing import List, Dict
from langchain_huggingface import HuggingFaceEmbeddings # type: ignore
from langchain_chroma import Chroma # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
# from langchain.schema import Document
from app.config import get_settings
import os

settings = get_settings()

# Initialize embeddings 

_embeddings = None

def get_embeddings():
    """Get or create embeddings model"""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL)
        
    return _embeddings

async def create_vector_store(text: str, file_id: str) -> Dict:
    """
    Create vector store from text
    
    Args:
        text: Full text from PDF
        file_id: Unique identifier for the document
        
    Returns:
        Dictionary with creation status and metadata
    """
    try:
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        # Create documents
        chunks= text_splitter.split_text(text)
        documents= [
            Document(
                page_content=chunks,
                metadata={"source": file_id, "chunk": i}
            )
            for i, chunks in enumerate(chunks)
        ]
        # Create vector store for this file
        collection_name = f"doc_{file_id}"
        persist_directory = os.path.join(settings.CHROMA_DIR, collection_name)
        
        vectorstore= Chroma.from_documents(
            documents=documents,
            embedding=get_embeddings(),
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        
        return{
           "success": True,
            "file_id": file_id,
            "num_chunks": len(chunks),
            "collection_name": collection_name
        }
    except Exception as e:
        raise Exception(f"Error creating vector store: {str(e)}")
    
async def query_vector_store(file_id: str, question: str, k: int = 3) -> List[Dict]:
    """
    Query vector store to find relevant chunks
    
    Args:
        file_id: Document identifier
        question: User's question
        k: Number of relevant chunks to retrieve
        
    Returns:
        List of relevant text chunks with metadata
    """
    try:
        collection_name = f"doc_{file_id}"
        persist_directory = os.path.join(settings.CHROMA_DIR, collection_name)
        
        # Check if vector store exists
        if not os.path.exists(persist_directory):
            raise ValueError(f"No vector store found for file_id: {file_id}")
        
        # Load vector store
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=get_embeddings(),
            collection_name=collection_name
        )
        
        # Search for relevant chunks
        results = vectorstore.similarity_search_with_score(question, k=k)
        
        # Format results
        relevant_chunks = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": float(score)
            }
            for doc, score in results
        ]
        
        return relevant_chunks
        
    except Exception as e:
        raise Exception(f"Error querying vector store: {str(e)}")