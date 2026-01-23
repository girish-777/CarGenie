"""
Alert model for price drop and listing alerts
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Alert(Base):
    """User alerts for price drops and new listings"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    alert_type = Column(String, nullable=False)  # price_drop, new_listing, custom
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)  # Nullable for custom alerts
    
    # Alert criteria
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    max_price = Column(Float, nullable=True)
    min_year = Column(Integer, nullable=True)
    max_mileage = Column(Integer, nullable=True)
    fuel_type = Column(String, nullable=True)
    
    # Additional criteria as JSON
    custom_criteria = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    car = relationship("Car", foreign_keys=[car_id])

