"""
Review model for car reviews (for AI summarization)
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Integer as SQLInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Review(Base):
    """Car reviews"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous reviews
    
    rating = Column(SQLInteger, nullable=False)  # 1-5 stars
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    
    # AI-generated summary (populated later)
    ai_summary = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    car = relationship("Car", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

