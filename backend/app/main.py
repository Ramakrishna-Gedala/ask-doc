# FastAPI Application Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging

from app.core.config import settings
from app.db.database import init_db
from app.api import auth_routes, document_routes, query_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Multi-tenant AI Document Q&A System with RAG"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Initialize database on app startup"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Application started successfully")


# Include routers
app.include_router(auth_routes.router)
app.include_router(document_routes.router)
app.include_router(query_routes.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Ask-Doc API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
