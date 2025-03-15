import os
from typing import List, Dict, Any
import logging

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, documents_path: str = None):
        self.documents_path = documents_path or settings.DOCUMENTS_PATH
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def load_pdf_documents(self) -> List[Dict[str, Any]]:
        """Load PDF documents from the specified directory"""
        logger.info(f"Loading PDF documents from {self.documents_path}")
        
        if not os.path.exists(self.documents_path):
            logger.warning(f"Documents directory {self.documents_path} does not exist, creating it")
            os.makedirs(self.documents_path, exist_ok=True)
            return []
        
        try:
            # Use DirectoryLoader to load all PDF files in the directory
            loader = DirectoryLoader(
                self.documents_path,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents successfully")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into smaller chunks for better embedding"""
        if not documents:
            logger.warning("No documents to split")
            return []
        
        try:
            split_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
            return split_docs
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            return documents  # Return original documents if splitting fails
    
    def process_documents(self) -> List[Dict[str, Any]]:
        """Load and process all documents"""
        documents = self.load_pdf_documents()
        if documents:
            return self.split_documents(documents)
        return []

# Function to get processed documents
def get_processed_documents() -> List[Dict[str, Any]]:
    processor = DocumentProcessor()
    return processor.process_documents()