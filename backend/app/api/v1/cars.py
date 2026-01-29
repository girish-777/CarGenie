"""
Car listings API endpoints
"""
import logging
import re
from difflib import SequenceMatcher
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from typing import Optional, List
from app.db.database import get_db
from app.models import Car, CarSpec, CarScore
from app.schemas.car import CarResponse, CarListResponse, CarDetailResponse, CarBase
from app.api.v1.auth import get_admin_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

_token_splitter = re.compile(r"[^a-zA-Z0-9]+")


def _normalize_for_match(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def _similarity(a: str, b: str) -> float:
    # SequenceMatcher returns 0..1
    return SequenceMatcher(None, a, b).ratio()


def _best_fuzzy_candidate(search_term: str, candidates: List[str]) -> tuple[Optional[str], float]:
    """
    Return (best_candidate, score). Score is 0..1.
    candidates are raw strings; matching uses normalized forms.
    """
    s_norm = _normalize_for_match(search_term)
    if not s_norm:
        return None, 0.0

    best = None
    best_score = 0.0
    for c in candidates:
        c_norm = _normalize_for_match(c)
        if not c_norm:
            continue
        score = _similarity(s_norm, c_norm)
        if score > best_score:
            best_score = score
            best = c
    return best, best_score


@router.get("/", response_model=CarListResponse)
def get_cars(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(12, ge=1, le=100, description="Items per page"),
    make: Optional[str] = Query(None, description="Filter by make"),
    model: Optional[str] = Query(None, description="Filter by model"),
    min_year: Optional[int] = Query(None, description="Minimum year"),
    max_year: Optional[int] = Query(None, description="Maximum year"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    fuel_type: Optional[str] = Query(None, description="Filter by fuel type"),
    transmission: Optional[str] = Query(None, description="Filter by transmission"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    search: Optional[str] = Query(None, description="Search in make, model, description"),
    sort_by: Optional[str] = Query("created_at", description="Sort by: price, year, mileage, created_at"),
    sort_order: Optional[str] = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """Get list of cars with filtering and pagination"""
    logger.info(f"[DEBUG] get_cars: Request received - page={page}, page_size={page_size}, make={make}, search={search}, sort_by={sort_by}")
    
    # Start with base query
    query = db.query(Car).filter(Car.is_available == True)
    logger.debug(f"[DEBUG] get_cars: Base query created")
    
    # Apply filters
    if make:
        query = query.filter(Car.make.ilike(f"%{make}%"))
    
    if model:
        query = query.filter(Car.model.ilike(f"%{model}%"))
    
    if min_year:
        query = query.filter(Car.year >= min_year)
    
    if max_year:
        query = query.filter(Car.year <= max_year)
    
    if min_price:
        query = query.filter(Car.price >= min_price)
    
    if max_price:
        query = query.filter(Car.price <= max_price)
    
    if fuel_type:
        query = query.filter(Car.fuel_type == fuel_type)
    
    if transmission:
        query = query.filter(Car.transmission == transmission)
    
    if condition:
        query = query.filter(Car.condition == condition)
    
    # Search functionality (with typo tolerance)
    original_search: Optional[str] = search.strip() if isinstance(search, str) and search.strip() else None
    corrected_search: Optional[str] = None
    correction_score: Optional[float] = None

    def _apply_search(q, term: str):
        sf = or_(
            Car.make.ilike(f"%{term}%"),
            Car.model.ilike(f"%{term}%"),
            Car.description.ilike(f"%{term}%"),
        )
        return q.filter(sf)

    if original_search:
        query = _apply_search(query, original_search)

    # Get total count for initial query
    total = query.count()
    logger.debug(f"[DEBUG] get_cars: Total cars matching filters: {total}")

    # If no results, try word-by-word fuzzy correction (Google-like "Did you mean")
    if total == 0 and original_search:
        # Tokenize the search query into words
        search_tokens = [t.strip() for t in _token_splitter.split(original_search) if t.strip()]
        
        if len(search_tokens) > 0:
            # Build vocabulary from all makes, models, and description words from all cars
            logger.debug("[DEBUG] get_cars: Building vocabulary from car data...")
            
            # Get all makes and models
            makes = [m[0] for m in db.query(Car.make).filter(Car.is_available == True).distinct().all() if m[0]]
            models = [m[0] for m in db.query(Car.model).filter(Car.is_available == True).distinct().all() if m[0]]
            
            # Get all descriptions and extract words
            descriptions = [d[0] for d in db.query(Car.description).filter(
                Car.is_available == True,
                Car.description.isnot(None)
            ).distinct().all() if d[0]]
            
            # Build vocabulary set from makes, models, and description words
            vocabulary_set = set()
            
            # Add makes and models as whole words
            for val in makes + models:
                if val:
                    vocabulary_set.add(val)
                    # Also add tokenized parts
                    parts = [p for p in _token_splitter.split(str(val)) if p and len(_normalize_for_match(p)) >= 3]
                    vocabulary_set.update(parts)
            
            # Extract words from descriptions (minimum 3 chars after normalization)
            for description_text in descriptions:
                if description_text:
                    desc_tokens = [t for t in _token_splitter.split(str(description_text)) if t]
                    for token in desc_tokens:
                        norm_token = _normalize_for_match(token)
                        if len(norm_token) >= 3:  # Only meaningful words
                            vocabulary_set.add(token)
            
            vocabulary = list(vocabulary_set)
            logger.debug(f"[DEBUG] get_cars: Vocabulary built with {len(vocabulary)} unique tokens")
            
            # Correct each token individually
            corrected_tokens = []
            overall_min_score = 1.0
            
            for token in search_tokens:
                token_norm = _normalize_for_match(token)
                
                # Skip very short tokens
                if len(token_norm) < 2:
                    corrected_tokens.append(token)
                    continue
                
                # Find best fuzzy match for this token
                best_match, score = _best_fuzzy_candidate(token, vocabulary)
                
                # Threshold: only correct when "close enough"
                # Allow common short typos like "binz" -> "benz", "tuyata" -> "toyota"
                threshold = 0.74 if len(token_norm) <= 4 else 0.72
                
                if best_match and score >= threshold and _normalize_for_match(best_match) != token_norm:
                    corrected_tokens.append(best_match)
                    overall_min_score = min(overall_min_score, score)
                    logger.debug(f"[DEBUG] get_cars: Corrected token '{token}' -> '{best_match}' (score={score:.3f})")
                else:
                    # Keep original token if no good match found
                    corrected_tokens.append(token)
            
            # Reconstruct corrected search string
            if corrected_tokens != search_tokens:
                corrected_search = " ".join(corrected_tokens)
                correction_score = float(round(overall_min_score, 3))
                logger.info(f"[DEBUG] get_cars: Applying fuzzy correction '{original_search}' -> '{corrected_search}' (min_score={correction_score})")

                # Re-run search with corrected terms (but keep other filters)
                query2 = db.query(Car).filter(Car.is_available == True)
                # Re-apply filters (same as above)
                if make:
                    query2 = query2.filter(Car.make.ilike(f"%{make}%"))
                if model:
                    query2 = query2.filter(Car.model.ilike(f"%{model}%"))
                if min_year:
                    query2 = query2.filter(Car.year >= min_year)
                if max_year:
                    query2 = query2.filter(Car.year <= max_year)
                if min_price:
                    query2 = query2.filter(Car.price >= min_price)
                if max_price:
                    query2 = query2.filter(Car.price <= max_price)
                if fuel_type:
                    query2 = query2.filter(Car.fuel_type == fuel_type)
                if transmission:
                    query2 = query2.filter(Car.transmission == transmission)
                if condition:
                    query2 = query2.filter(Car.condition == condition)

                query2 = _apply_search(query2, corrected_search)
                total = query2.count()
                query = query2
                logger.debug(f"[DEBUG] get_cars: Total after correction: {total}")
    
    # Apply sorting
    valid_sort_fields = {
        "price": Car.price,
        "year": Car.year,
        "mileage": Car.mileage,
        "created_at": Car.created_at
    }
    
    sort_field = valid_sort_fields.get(sort_by, Car.created_at)
    logger.debug(f"[DEBUG] get_cars: Sorting by {sort_by} ({sort_order})")
    
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # Apply pagination
    offset = (page - 1) * page_size
    logger.debug(f"[DEBUG] get_cars: Pagination - offset={offset}, limit={page_size}")
    cars = query.offset(offset).limit(page_size).all()
    
    logger.info(f"[DEBUG] get_cars: Returning {len(cars)} cars (page {page} of {(total + page_size - 1) // page_size})")
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "cars": cars,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "original_search": original_search,
        "corrected_search": corrected_search,
        "correction_score": correction_score,
    }


@router.get("/makes/list", response_model=List[str])
def get_makes(db: Session = Depends(get_db)):
    """Get list of all unique car makes"""
    makes = db.query(Car.make).distinct().order_by(Car.make).all()
    return [make[0] for make in makes]


@router.get("/fuel-types/list", response_model=List[str])
def get_fuel_types(db: Session = Depends(get_db)):
    """Get list of all unique fuel types"""
    fuel_types = db.query(Car.fuel_type).distinct().order_by(Car.fuel_type).all()
    return [ft[0] for ft in fuel_types]


@router.get("/{car_id}", response_model=CarDetailResponse)
def get_car_detail(car_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific car"""
    logger.info(f"[DEBUG] get_car_detail: Request for car ID {car_id}")
    car = db.query(Car).filter(Car.id == car_id).first()
    
    if not car:
        logger.warning(f"[DEBUG] get_car_detail: Car ID {car_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    logger.info(f"[DEBUG] get_car_detail: Car found - {car.make} {car.model} (ID: {car.id})")
    return car


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Delete a car (Admin only)"""
    logger.info(f"[Admin] Deleting car ID {car_id}")
    
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    db.delete(car)
    db.commit()
    
    logger.info(f"[Admin] Car {car_id} deleted successfully")
    return None


@router.patch("/{car_id}/price", response_model=CarResponse)
def update_car_price(
    car_id: int,
    new_price: float = Query(..., ge=0, description="New price"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """Update car price (Admin only)"""
    logger.info(f"[Admin] Updating price for car ID {car_id} to ${new_price}")
    
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Store original image_urls to preserve them
    original_image_urls = car.image_urls
    
    old_price = car.price
    car.price = new_price
    
    # Ensure image_urls are preserved (shouldn't change, but being explicit)
    if car.image_urls != original_image_urls:
        car.image_urls = original_image_urls
    
    # Record price change in PriceHistory for alert system
    from app.models import PriceHistory
    price_history = PriceHistory(car_id=car.id, price=new_price)
    db.add(price_history)
    
    db.commit()
    db.refresh(car)
    
    # Double-check image_urls are preserved after refresh
    if car.image_urls != original_image_urls:
        logger.warning(f"[Admin] Image URLs changed after price update, restoring original")
        car.image_urls = original_image_urls
        db.commit()
        db.refresh(car)
    
    # Alert feature removed
    
    logger.info(f"[Admin] Car {car_id} price updated from ${old_price} to ${new_price}")
    logger.debug(f"[Admin] Image URLs preserved: {car.image_urls}")
    return car

