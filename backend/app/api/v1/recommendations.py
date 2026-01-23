"""
Personalized recommendations API endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Car, Favorite
from app.models.user import User
from app.core.embeddings import EmbeddingsService
from app.core.vectordb import VectorDB
from app.core.security import decode_access_token
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
embeddings_service = EmbeddingsService()
vectordb = VectorDB()

# Optional auth scheme for recommendations (no error if missing)
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    auto_error=False
)


class RecommendationResponse(BaseModel):
    """Response for car recommendation"""
    car_id: int
    make: str
    model: str
    year: int
    price: float
    fuel_type: str
    transmission: str
    mileage: int
    image_urls: Optional[List[str]] = []
    similarity_score: Optional[float] = None
    recommendation_reason: Optional[str] = None

    class Config:
        from_attributes = True


class RecommendationsResponse(BaseModel):
    """Response for recommendations list"""
    recommendations: List[RecommendationResponse]
    total: int
    user_preferences: Optional[dict] = None


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        if payload is None:
            logger.debug("[Recommendations] Token decode failed")
            return None

        email: str = payload.get("sub")
        if email is None:
            logger.debug("[Recommendations] Token missing subject")
            return None

        user = db.query(User).filter(User.email == email).first()
        if user and user.is_active:
            return user
        return None
    except Exception as e:
        logger.debug(f"[Recommendations] Error getting user: {e}")
        return None


@router.get("/recommendations", response_model=RecommendationsResponse, status_code=status.HTTP_200_OK)
def get_personalized_recommendations(
    n_results: int = Query(10, ge=1, le=20),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized car recommendations based on user preferences
    
    For logged-in users:
    - Analyzes favorite cars to understand preferences
    - Uses vector similarity to find similar cars
    - Considers price range, make, fuel type preferences
    
    For non-logged-in users:
    - Returns popular/recent cars
    """
    logger.info(f"[AI Recommendations] Getting recommendations for user: {current_user.id if current_user else 'anonymous'}")
    
    recommendations = []
    user_preferences = None
    
    if current_user:
        # Get user's favorite cars
        favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
        favorite_car_ids = [f.car_id for f in favorites]
        
        if favorite_car_ids:
            # Get favorite cars from database
            favorite_cars = db.query(Car).filter(Car.id.in_(favorite_car_ids)).all()
            
            # Analyze user preferences
            makes = [car.make for car in favorite_cars]
            fuel_types = [car.fuel_type for car in favorite_cars]
            prices = [car.price for car in favorite_cars]
            transmissions = [car.transmission for car in favorite_cars]
            
            # Calculate preferences
            user_preferences = {
                "preferred_makes": list(set(makes)),
                "preferred_fuel_types": list(set(fuel_types)),
                "preferred_transmissions": list(set(transmissions)),
                "price_range": {
                    "min": min(prices) if prices else None,
                    "max": max(prices) if prices else None,
                    "avg": sum(prices) / len(prices) if prices else None
                },
                "favorite_count": len(favorite_cars)
            }
            
            logger.info(f"[AI Recommendations] User preferences: {user_preferences}")
            
            # Get recommendations using vector similarity
            recommended_car_ids = set()
            
            for favorite_car in favorite_cars:
                try:
                    # Get or generate embedding for favorite car
                    embedding = vectordb.get_car_embedding(favorite_car.id)
                    
                    if not embedding:
                        # Generate embedding if not exists
                        embedding = embeddings_service.generate_car_embedding(
                            make=favorite_car.make,
                            model=favorite_car.model,
                            year=favorite_car.year,
                            description=favorite_car.description,
                            fuel_type=favorite_car.fuel_type,
                            transmission=favorite_car.transmission
                        )
                        
                        if embedding:
                            metadata = {
                                "make": favorite_car.make,
                                "model": favorite_car.model,
                                "year": favorite_car.year,
                                "price": favorite_car.price,
                                "fuel_type": favorite_car.fuel_type,
                                "transmission": favorite_car.transmission,
                                "description": favorite_car.description or ""
                            }
                            vectordb.add_car_embedding(favorite_car.id, embedding, metadata)
                    
                    if embedding:
                        # Find similar cars (exclude favorites)
                        similar_results = vectordb.search_similar_cars(
                            query_embedding=embedding,
                            n_results=n_results + len(favorite_car_ids)
                        )
                        
                        # Filter out favorite cars
                        for result in similar_results:
                            car_id = result["car_id"]
                            if car_id not in favorite_car_ids and car_id not in recommended_car_ids:
                                recommended_car_ids.add(car_id)
                                if len(recommended_car_ids) >= n_results:
                                    break
                        
                        if len(recommended_car_ids) >= n_results:
                            break
                            
                except Exception as e:
                    logger.warning(f"[AI Recommendations] Error getting similar cars: {e}")
                    continue
            
            # If we don't have enough, fill with preference-based
            if len(recommended_car_ids) < n_results:
                query = db.query(Car).filter(
                    Car.is_available == True,
                    Car.id.notin_(favorite_car_ids + list(recommended_car_ids))
                )
                
                if user_preferences["preferred_makes"]:
                    query = query.filter(Car.make.in_(user_preferences["preferred_makes"]))
                
                if user_preferences["price_range"]["avg"]:
                    price_margin = user_preferences["price_range"]["avg"] * 0.2
                    min_price = user_preferences["price_range"]["avg"] - price_margin
                    max_price = user_preferences["price_range"]["avg"] + price_margin
                    query = query.filter(Car.price >= min_price, Car.price <= max_price)
                
                additional_cars = query.limit(n_results - len(recommended_car_ids)).all()
                for car in additional_cars:
                    recommended_car_ids.add(car.id)
            
            # Ensure at least 3 recommendations (fill with any available cars if needed)
            if len(recommended_car_ids) < 3:
                fallback_query = db.query(Car).filter(
                    Car.is_available == True,
                    Car.id.notin_(favorite_car_ids + list(recommended_car_ids))
                ).limit(3 - len(recommended_car_ids))
                
                fallback_cars = fallback_query.all()
                for car in fallback_cars:
                    recommended_car_ids.add(car.id)
            
            # Get full car details
            if recommended_car_ids:
                # Ensure we have at least 3 recommendations
                num_needed = max(3, n_results)
                recommended_cars = db.query(Car).filter(Car.id.in_(list(recommended_car_ids)[:num_needed])).all()
                
                # If we still don't have enough, fill with any available cars
                if len(recommended_cars) < 3:
                    additional_needed = 3 - len(recommended_cars)
                    existing_ids = [c.id for c in recommended_cars] + favorite_car_ids
                    additional_cars = db.query(Car).filter(
                        Car.is_available == True,
                        Car.id.notin_(existing_ids)
                    ).limit(additional_needed).all()
                    recommended_cars.extend(additional_cars)
                
                for car in recommended_cars:
                    similarity_score = None
                    recommendation_reason = None
                    
                    # Find best matching favorite
                    best_match = None
                    for favorite_car in favorite_cars:
                        if car.make == favorite_car.make:
                            best_match = favorite_car
                            similarity_score = 85.0
                            break
                    
                    if best_match:
                        recommendation_reason = f"Similar to your favorite {best_match.year} {best_match.make} {best_match.model}"
                    elif car.make in user_preferences["preferred_makes"]:
                        recommendation_reason = f"Matches your preference for {car.make}"
                    else:
                        recommendation_reason = "Based on your preferences"
                    
                    recommendations.append(RecommendationResponse(
                        car_id=car.id,
                        make=car.make,
                        model=car.model,
                        year=car.year,
                        price=car.price,
                        fuel_type=car.fuel_type,
                        transmission=car.transmission,
                        mileage=car.mileage,
                        image_urls=car.image_urls or [],
                        similarity_score=similarity_score,
                        recommendation_reason=recommendation_reason
                    ))
        else:
            # No favorites - return popular cars (ensure at least 3)
            num_needed = max(3, n_results)
            popular_cars = db.query(Car).filter(
                Car.is_available == True
            ).order_by(Car.created_at.desc()).limit(num_needed).all()
            
            for car in popular_cars:
                recommendations.append(RecommendationResponse(
                    car_id=car.id,
                    make=car.make,
                    model=car.model,
                    year=car.year,
                    price=car.price,
                    fuel_type=car.fuel_type,
                    transmission=car.transmission,
                    mileage=car.mileage,
                    image_urls=car.image_urls or [],
                    recommendation_reason="Popular listing"
                ))
    else:
        # Anonymous user - return popular cars (ensure at least 3)
        num_needed = max(3, n_results)
        popular_cars = db.query(Car).filter(
            Car.is_available == True
        ).order_by(Car.created_at.desc()).limit(num_needed).all()
        
        for car in popular_cars:
            recommendations.append(RecommendationResponse(
                car_id=car.id,
                make=car.make,
                model=car.model,
                year=car.year,
                price=car.price,
                fuel_type=car.fuel_type,
                transmission=car.transmission,
                mileage=car.mileage,
                image_urls=car.image_urls or [],
                recommendation_reason="Popular listing"
            ))
    
    # Ensure at least 3 recommendations are returned
    if len(recommendations) < 3:
        logger.warning(f"[AI Recommendations] Only {len(recommendations)} recommendations available, trying to get more...")
        # Get any additional available cars
        existing_ids = [r.car_id for r in recommendations]
        additional_cars = db.query(Car).filter(
            Car.is_available == True,
            Car.id.notin_(existing_ids)
        ).limit(3 - len(recommendations)).all()
        
        for car in additional_cars:
            recommendations.append(RecommendationResponse(
                car_id=car.id,
                make=car.make,
                model=car.model,
                year=car.year,
                price=car.price,
                fuel_type=car.fuel_type,
                transmission=car.transmission,
                mileage=car.mileage,
                image_urls=car.image_urls or [],
                recommendation_reason="Popular listing"
            ))
    
    logger.info(f"[AI Recommendations] Returning {len(recommendations)} recommendations")
    
    return RecommendationsResponse(
        recommendations=recommendations,
        total=len(recommendations),
        user_preferences=user_preferences
    )

