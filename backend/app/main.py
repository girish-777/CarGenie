"""
Main FastAPI application
"""
import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, cars, favorites, reviews, ai, recommendations, predictions
from app.core.config import settings
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Automobile Website API",
    description="Backend API for AI-powered automobile website",
    version="1.0.0"
)

# Configure CORS
# Ensure CORS_ORIGINS is a list
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

# Add explicit frontend URL if not already present
frontend_url = "https://cargenie-frontend.onrender.com"
if frontend_url not in cors_origins:
    cors_origins.append(frontend_url)

logger.info(f"CORS Origins configured: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(cars.router, prefix="/api/v1/cars", tags=["Cars"])
app.include_router(favorites.router, prefix="/api/v1/favorites", tags=["Favorites"])
app.include_router(reviews.router, prefix="/api/v1/reviews", tags=["Reviews"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered Automobile Website API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/v1/health")
def api_health_check():
    """Detailed health check with database connection test"""
    from sqlalchemy import text
    from app.db.database import SessionLocal
    
    db_status = "unknown"
    try:
        db = SessionLocal()
        # Test database connection
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Database health check failed: {e}")
    
    return {
        "status": "healthy",
        "database": db_status,
        "api": "operational"
    }


# Alert feature removed

