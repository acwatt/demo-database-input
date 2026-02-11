"""
FastAPI application for demo-database-input.

Provides REST API for managing work experience projects.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from .routes import router
import sys

# Add parent directory to path for database imports
sys.path.append(str(Path(__file__).parent.parent))
from database.init_db import init_database
from database.db_utils import ensure_database_exists

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Demo Database Input API",
    description="REST API for managing work experience projects",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup.

    - Ensure database exists
    - Initialize if needed
    - Log startup information
    """
    logger.info("Starting up application...")

    # Check if database exists
    db_exists = await ensure_database_exists()

    if not db_exists:
        logger.warning("Database not found. Initializing...")
        success = init_database()
        if not success:
            logger.error("Failed to initialize database!")
            raise RuntimeError("Database initialization failed")
        logger.info("Database initialized successfully")
    else:
        logger.info("Database verified successfully")

    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down application...")
    # Add any cleanup tasks here (e.g., close connection pools)
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """
    Root endpoint - health check.

    Returns:
        API status and basic info
    """
    return {
        "status": "online",
        "message": "Demo Database Input API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Health status
    """
    # Check database connectivity
    db_ok = await ensure_database_exists()

    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected"
    }


# Serve frontend static files (after frontend is created)
# Uncomment when frontend is ready:
# frontend_path = Path(__file__).parent.parent / "frontend"
# if frontend_path.exists():
#     app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
