"""
Favorites API endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Favorite, Car
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.schemas.favorite import FavoriteResponse, FavoriteCreate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a car to user's favorites"""
    logger.info(f"[Favorites] User {current_user.id} adding car {favorite_data.car_id} to favorites")
    
    # Check if car exists
    car = db.query(Car).filter(Car.id == favorite_data.car_id).first()
    if not car:
        logger.warning(f"[Favorites] Car {favorite_data.car_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Check if already favorited
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.car_id == favorite_data.car_id
    ).first()
    
    if existing_favorite:
        logger.info(f"[Favorites] Car {favorite_data.car_id} already in favorites for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car is already in favorites"
        )
    
    # Create favorite
    favorite = Favorite(
        user_id=current_user.id,
        car_id=favorite_data.car_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    logger.info(f"[Favorites] Car {favorite_data.car_id} added to favorites for user {current_user.id}")
    return FavoriteResponse(
        id=favorite.id,
        user_id=favorite.user_id,
        car_id=favorite.car_id,
        created_at=favorite.created_at,
        car=car
    )


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a car from user's favorites"""
    logger.info(f"[Favorites] User {current_user.id} removing car {car_id} from favorites")
    
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.car_id == car_id
    ).first()
    
    if not favorite:
        logger.warning(f"[Favorites] Favorite not found for user {current_user.id}, car {car_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    db.delete(favorite)
    db.commit()
    logger.info(f"[Favorites] Favorite removed successfully")
    return None


@router.get("/", response_model=List[FavoriteResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all favorites for current user"""
    logger.info(f"[Favorites] User {current_user.id} requesting favorites")
    
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).all()
    
    result = []
    for fav in favorites:
        car = db.query(Car).filter(Car.id == fav.car_id).first()
        if car:
            result.append(FavoriteResponse(
                id=fav.id,
                user_id=fav.user_id,
                car_id=fav.car_id,
                created_at=fav.created_at,
                car=car
            ))
    
    return result


@router.get("/check/{car_id}")
def check_favorite(
    car_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if a car is in user's favorites"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.car_id == car_id
    ).first()
    
    return {"is_favorite": favorite is not None}

