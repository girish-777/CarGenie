"""
Reviews API endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.database import get_db
from app.models import Review, Car
from app.models.user import User
from app.api.v1.auth import get_current_user, get_current_active_user
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse
from app.core.embeddings import EmbeddingsService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize embeddings service for review summarization
embeddings_service = EmbeddingsService()


def generate_review_summary(car_id: int):
    """Background task to generate AI summary for car reviews"""
    from app.db.database import SessionLocal
    
    # Create a new database session for the background task
    db = SessionLocal()
    try:
        # Get all reviews for the car
        reviews = db.query(Review).filter(Review.car_id == car_id).all()
        
        if len(reviews) < 2:
            logger.info(f"[Reviews] Not enough reviews ({len(reviews)}) to generate summary for car {car_id}")
            return
        
        # Extract review texts
        review_texts = [
            f"Rating: {r.rating}/5. {r.title or ''} {r.content}"
            for r in reviews
        ]
        
        # Generate summary
        summary = embeddings_service.summarize_reviews(review_texts, max_length=200)
        
        if summary:
            # Update all reviews with the summary (or we could store it on the car model)
            # For now, we'll update the most recent review's ai_summary field
            # In a production system, you might want a separate table for car summaries
            latest_review = reviews[-1]
            latest_review.ai_summary = summary
            db.commit()
            logger.info(f"[Reviews] Generated AI summary for car {car_id}")
        else:
            logger.warning(f"[Reviews] Failed to generate summary for car {car_id}")
    except Exception as e:
        logger.error(f"[Reviews] Error generating summary for car {car_id}: {e}")
        db.rollback()
    finally:
        db.close()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new review for a car"""
    logger.info(f"[DEBUG] create_review: User {current_user.id} creating review for car {review_data.car_id}")
    
    # Check if car exists
    car = db.query(Car).filter(Car.id == review_data.car_id).first()
    if not car:
        logger.warning(f"[DEBUG] create_review: Car {review_data.car_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Check if user already reviewed this car
    existing_review = db.query(Review).filter(
        Review.car_id == review_data.car_id,
        Review.user_id == current_user.id
    ).first()
    
    if existing_review:
        logger.warning(f"[DEBUG] create_review: User {current_user.id} already reviewed car {review_data.car_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You have already reviewed this car. You can edit your existing review (ID: {existing_review.id}) instead."
        )
    
    # Create review
    logger.debug(f"[DEBUG] create_review: Creating new review")
    review = Review(
        car_id=review_data.car_id,
        user_id=current_user.id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    logger.info(f"[DEBUG] create_review: Review created successfully (ID: {review.id})")
    
    # Trigger background task to generate AI summary if we have enough reviews
    background_tasks.add_task(generate_review_summary, review_data.car_id)
    
    return review


@router.get("/car/{car_id}", response_model=ReviewListResponse)
def get_car_reviews(
    car_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific car"""
    logger.info(f"[DEBUG] get_car_reviews: Getting reviews for car {car_id}")
    
    # Check if car exists
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        logger.warning(f"[DEBUG] get_car_reviews: Car {car_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Get reviews
    reviews_query = db.query(Review).filter(Review.car_id == car_id).order_by(desc(Review.created_at))
    total = reviews_query.count()
    reviews = reviews_query.offset(skip).limit(limit).all()
    
    # Calculate average rating
    avg_rating = db.query(func.avg(Review.rating)).filter(Review.car_id == car_id).scalar()
    
    logger.info(f"[DEBUG] get_car_reviews: Found {total} reviews for car {car_id}, returning {len(reviews)}")
    
    return ReviewListResponse(
        reviews=reviews,
        total=total,
        average_rating=float(avg_rating) if avg_rating else None
    )


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific review by ID"""
    logger.info(f"[DEBUG] get_review: Getting review {review_id}")
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        logger.warning(f"[DEBUG] get_review: Review {review_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a review (only by the author)"""
    logger.info(f"[DEBUG] update_review: User {current_user.id} updating review {review_id}")
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        logger.warning(f"[DEBUG] update_review: Review {review_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user owns the review
    if review.user_id != current_user.id:
        logger.warning(f"[DEBUG] update_review: User {current_user.id} does not own review {review_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    # Update review
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    logger.info(f"[DEBUG] update_review: Review {review_id} updated successfully")
    
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a review (only by the author)"""
    logger.info(f"[DEBUG] delete_review: User {current_user.id} deleting review {review_id}")
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        logger.warning(f"[DEBUG] delete_review: Review {review_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Check if user owns the review
    if review.user_id != current_user.id:
        logger.warning(f"[DEBUG] delete_review: User {current_user.id} does not own review {review_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    db.delete(review)
    db.commit()
    logger.info(f"[DEBUG] delete_review: Review {review_id} deleted successfully")
    return None

