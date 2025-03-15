import uvicorn
import logging
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from app.core.config import settings
from app.core.database import Base, engine
from app.api.routes import router as api_router
from app.rag.generator import ResponseGenerator
from app.rag.embedder import initialize_vector_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Rumah Kreatif Toba Chatbot API",
    description="API untuk chatbot Rumah Kreatif Toba menggunakan Retrieval-Augmented Generation (RAG)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str

# Initialize RAG components on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing vector database...")
    initialize_vector_db()
    logger.info("Application startup complete")

# Initialize response generator
response_generator = ResponseGenerator()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for the chatbot
    """
    try:
        user_message = request.message
        logger.info(f"Received message: {user_message}")
        
        # Generate response
        response = response_generator.generate_response(user_message)
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Rumah Kreatif Toba Chatbot API",
        "docs": "/docs",
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )