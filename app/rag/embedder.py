import os
import logging
from typing import List, Dict, Any

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
    
from app.rag.document_loader import get_processed_documents
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentEmbedder:
    def __init__(self, vector_db_path: str = None):
        self.vector_db_path = vector_db_path or settings.VECTOR_DB_PATH
        
        # Initialize embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
    
    def create_vector_db(self, documents: List[Dict[str, Any]]) -> Chroma:
        """Create or update vector database from documents"""
        if not documents:
            logger.warning("No documents provided to create vector database")
            return None
        
        # Create directory if it doesn't exist
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        try:
            # Create vector store
            vector_db = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.vector_db_path
            )
            
            # Persist the database
            vector_db.persist()
            logger.info(f"Vector database created/updated successfully at {self.vector_db_path}")
            return vector_db
        except Exception as e:
            logger.error(f"Error creating vector database: {str(e)}")
            return None
    
    def load_vector_db(self) -> Chroma:
        """Load existing vector database"""
        if not os.path.exists(self.vector_db_path):
            logger.warning(f"Vector database directory {self.vector_db_path} does not exist")
            return None
        
        try:
            vector_db = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info(f"Vector database loaded successfully from {self.vector_db_path}")
            return vector_db
        except Exception as e:
            logger.error(f"Error loading vector database: {str(e)}")
            return None

def initialize_vector_db():
    """Initialize or update the vector database"""
    embedder = DocumentEmbedder()
    
    # Try to load existing vector DB
    vector_db = embedder.load_vector_db()
    
    # If vector DB doesn't exist or is empty, create it
    if vector_db is None:
        documents = get_processed_documents()
        if documents:
            vector_db = embedder.create_vector_db(documents)
    
    return vector_db