"""
Pydantic schemas for request/response validation
"""
from app.schemas.user import User, UserCreate, UserInDB, UserResponse
from app.schemas.auth import Token, TokenData
from app.schemas.car import (
    CarResponse,
    CarListResponse,
    CarDetailResponse,
    CarSpecResponse,
    CarScoreResponse
)
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse

__all__ = [
    "User",
    "UserCreate",
    "UserInDB",
    "UserResponse",
    "Token",
    "TokenData",
    "CarResponse",
    "CarListResponse",
    "CarDetailResponse",
    "CarSpecResponse",
    "CarScoreResponse",
    "FavoriteCreate",
    "FavoriteResponse",
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewListResponse",
]

