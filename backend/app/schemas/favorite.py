"""
Favorite schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.car import CarResponse


class FavoriteCreate(BaseModel):
    """Schema for creating a favorite"""
    car_id: int = Field(..., description="Car ID to add to favorites")


class FavoriteResponse(BaseModel):
    """Schema for favorite response"""
    id: int
    user_id: int
    car_id: int
    created_at: datetime
    car: CarResponse
    
    class Config:
        from_attributes = True

