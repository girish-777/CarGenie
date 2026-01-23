"""
Price history model for tracking car price changes
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class PriceHistory(Base):
    """Track price changes for cars"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_car_recorded', 'car_id', 'recorded_at'),
    )
    
    # Relationships
    car = relationship("Car", back_populates="price_history")

