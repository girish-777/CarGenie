"""
Car models for listings and specifications
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Car(Base):
    """Car listing model"""
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    make = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    price = Column(Float, nullable=False)
    mileage = Column(Integer, nullable=False)
    fuel_type = Column(String, nullable=False)  # gasoline, diesel, electric, hybrid
    transmission = Column(String, nullable=False)  # manual, automatic, CVT
    color = Column(String, nullable=True)
    condition = Column(String, nullable=False)  # new, used, certified-pre-owned
    engine_condition = Column(String, nullable=True)  # excellent, good, fair
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    image_urls = Column(JSON, nullable=True)  # List of image URLs
    vin = Column(String, unique=True, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    specs = relationship("CarSpec", back_populates="car", uselist=False, cascade="all, delete-orphan")
    scores = relationship("CarScore", back_populates="car", uselist=False, cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="car", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="car", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="car", cascade="all, delete-orphan")


class CarSpec(Base):
    """Detailed car specifications"""
    __tablename__ = "car_specs"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), unique=True, nullable=False)
    
    # Engine
    engine_size = Column(Float, nullable=True)  # liters
    cylinders = Column(Integer, nullable=True)
    horsepower = Column(Integer, nullable=True)
    torque = Column(Integer, nullable=True)
    
    # Performance
    acceleration_0_60 = Column(Float, nullable=True)  # seconds
    top_speed = Column(Integer, nullable=True)  # mph
    mpg_city = Column(Float, nullable=True)
    mpg_highway = Column(Float, nullable=True)
    
    # Dimensions
    length = Column(Float, nullable=True)  # inches
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)  # lbs
    
    # Features
    seating_capacity = Column(Integer, nullable=True)
    doors = Column(Integer, nullable=True)
    drivetrain = Column(String, nullable=True)  # FWD, RWD, AWD, 4WD
    
    # Additional specs as JSON
    additional_specs = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    car = relationship("Car", back_populates="specs")


class CarScore(Base):
    """Reliability and safety scores for cars"""
    __tablename__ = "car_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), unique=True, nullable=False)
    
    reliability_score = Column(Float, nullable=True)  # 0-10
    safety_score = Column(Float, nullable=True)  # 0-10
    overall_score = Column(Float, nullable=True)  # 0-10
    
    # Detailed scores
    crash_test_rating = Column(String, nullable=True)  # NHTSA/IIHS rating
    predicted_reliability = Column(Float, nullable=True)  # 0-10
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    car = relationship("Car", back_populates="scores")

