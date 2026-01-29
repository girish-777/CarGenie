"""
Car schemas for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CarSpecBase(BaseModel):
    """Base car specification schema"""
    engine_size: Optional[float] = None
    cylinders: Optional[int] = None
    horsepower: Optional[int] = None
    torque: Optional[int] = None
    acceleration_0_60: Optional[float] = None
    top_speed: Optional[int] = None
    mpg_city: Optional[float] = None
    mpg_highway: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    seating_capacity: Optional[int] = None
    doors: Optional[int] = None
    drivetrain: Optional[str] = None


class CarSpecResponse(CarSpecBase):
    """Car specification response schema"""
    id: int
    car_id: int
    
    class Config:
        from_attributes = True


class CarScoreBase(BaseModel):
    """Base car score schema"""
    reliability_score: Optional[float] = None
    safety_score: Optional[float] = None
    overall_score: Optional[float] = None
    crash_test_rating: Optional[str] = None
    predicted_reliability: Optional[float] = None


class CarScoreResponse(CarScoreBase):
    """Car score response schema"""
    id: int
    car_id: int
    
    class Config:
        from_attributes = True


class CarBase(BaseModel):
    """Base car schema"""
    make: str
    model: str
    year: int
    price: float
    mileage: int
    fuel_type: str
    transmission: str
    color: Optional[str] = None
    condition: str
    engine_condition: Optional[str] = None  # excellent, good, fair
    location: Optional[str] = None
    description: Optional[str] = None
    image_urls: Optional[List[str]] = None
    vin: Optional[str] = None


class CarResponse(CarBase):
    """Car response schema"""
    id: int
    is_available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    specs: Optional[CarSpecResponse] = None
    scores: Optional[CarScoreResponse] = None
    
    class Config:
        from_attributes = True


class CarListResponse(BaseModel):
    """Car list response with pagination"""
    cars: List[CarResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    # Optional typo-tolerant search metadata
    original_search: Optional[str] = None
    corrected_search: Optional[str] = None
    correction_score: Optional[float] = None


class CarDetailResponse(CarResponse):
    """Car detail response with full information"""
    pass

