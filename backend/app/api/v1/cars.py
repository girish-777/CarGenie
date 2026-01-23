"""
Car listings API endpoints
"""
import logging
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
    
    # Search functionality
    if search:
        search_filter = or_(
            Car.make.ilike(f"%{search}%"),
            Car.model.ilike(f"%{search}%"),
            Car.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    logger.debug(f"[DEBUG] get_cars: Total cars matching filters: {total}")
    
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
        "total_pages": total_pages
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

