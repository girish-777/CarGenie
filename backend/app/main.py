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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Alert feature removed

