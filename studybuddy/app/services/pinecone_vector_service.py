"""
Pinecone Vector Service - Cloud vector storage (no RAM usage)
"""
from typing import List, Dict
from langchain_pinecone import PineconeVectorStore # type: ignore
from langchain_huggingface import HuggingFaceEmbeddings # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec # type: ignore
from app.config import get_settings
import time

settings = get_settings()

# Initialize Pinecone client
_pc= None
_embeddings= None

def get_pinecone_client():
    """Initialize Pinecone client"""
    global _pc
    if _pc is None:
        _pc= Pinecone(api_key=settings.PINECONE_API_KEY)
    return _pc

def get_embeddings():
    """Get embeddings model"""
    global _embeddings
    if _embeddings is None:
        _embeddings= HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings

def ensure_index_exists():
    """Create Pinecone index if it doesn't exist"""
    pc= get_pinecone_client()
    index_name= settings.PINECONE_INDEX_NAME
    
    existing_indexes= [idx.name for idx in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        time.sleep(10)  # Wait for index to be ready
    return pc.Index(index_name)

async def create_vector_store_pinecone(text: str, file_id: str) -> Dict:
    """
    Create vector store in Pinecone (cloud-based, no RAM usage)
    
    Args:
        text: Full text from PDF
        file_id: Unique identifier
        
    Returns:
        Creation status
    """
    try:
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(text)
        
        # Create documents with metadata
        documents = [
            Document(
                page_content=chunk,
                metadata={"source": file_id, "chunk": i}
            )
            for i, chunk in enumerate(chunks)
        ]
        # Ensure index exists
        ensure_index_exists()
        
        # Create vector store (uploads to Pinecone cloud)
        vectorstore = PineconeVectorStore.from_documents(
            documents=documents,
            embedding=get_embeddings(),
            index_name=settings.PINECONE_INDEX_NAME,
            namespace=file_id  # Each file gets its own namespace
        )
        return {
            "success": True,
            "file_id": file_id,
            "num_chunks": len(chunks),
            "storage": "pinecone_cloud"
        }
        
    except Exception as e:
        raise Exception(f"Error creating Pinecone vector store: {str(e)}")

async def query_vector_store_pinecone(file_id: str, question: str, k: int = 3) -> List[Dict]:
    """
    Query Pinecone vector store
    
    Args:
        file_id: Document identifier
        question: User's question
        k: Number of results
        
    Returns:
        Relevant chunks
    """
    try:
        # Connect to Pinecone
        vectorstore = PineconeVectorStore(
            index_name=settings.PINECONE_INDEX_NAME,
            embedding=get_embeddings(),
            namespace=file_id
        )
        
        # Search
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
        raise Exception(f"Error querying Pinecone: {str(e)}")

async def delete_file_vectors(file_id: str) -> bool:
    """
    Delete all vectors for a file (free up space)
    
    Args:
        file_id: File to delete
        
    Returns:
        Success status
    """
    try:
        pc = get_pinecone_client()
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Delete namespace (all vectors for this file)
        index.delete(namespace=file_id, delete_all=True)
        
        return True
    except Exception as e:
        print(f"Error deleting vectors: {e}")
        return False