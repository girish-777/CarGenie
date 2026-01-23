"""
Review schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    """Base review schema"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    content: str = Field(..., min_length=10, description="Review content")


class ReviewCreate(ReviewBase):
    """Schema for creating a review"""
    car_id: int = Field(..., description="ID of the car being reviewed")


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=10)


class ReviewResponse(ReviewBase):
    """Schema for review response"""
    id: int
    car_id: int
    user_id: Optional[int]
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Schema for list of reviews"""
    reviews: list[ReviewResponse]
    total: int
    average_rating: Optional[float] = None

