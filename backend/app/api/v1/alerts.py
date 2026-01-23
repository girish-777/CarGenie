"""
Alerts API endpoints and background agent
"""
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Alert, Car, User
from app.api.v1.auth import get_current_active_user
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)


class AlertCreate(BaseModel):
    """Schema for creating an alert"""
    alert_type: str = Field(..., description="Type: price_drop, new_listing, or custom")
    car_id: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    max_price: Optional[float] = None
    min_year: Optional[int] = None
    max_mileage: Optional[int] = None
    fuel_type: Optional[str] = None
    custom_criteria: Optional[dict] = None


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    alert_type: str
    car_id: Optional[int]
    make: Optional[str]
    model: Optional[str]
    max_price: Optional[float]
    min_year: Optional[int]
    max_mileage: Optional[int]
    fuel_type: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    logger.info(f"[Alerts] User {current_user.id} creating alert: {alert_data.alert_type}")
    
    alert = Alert(
        user_id=current_user.id,
        alert_type=alert_data.alert_type,
        car_id=alert_data.car_id,
        make=alert_data.make,
        model=alert_data.model,
        max_price=alert_data.max_price,
        min_year=alert_data.min_year,
        max_mileage=alert_data.max_mileage,
        fuel_type=alert_data.fuel_type,
        custom_criteria=alert_data.custom_criteria
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    # For price_drop alerts with car_id, record current price in PriceHistory
    if alert.alert_type == "price_drop" and alert.car_id:
        from app.models import PriceHistory
        car = db.query(Car).filter(Car.id == alert.car_id).first()
        if car:
            # Check if price already recorded today (avoid duplicates)
            from datetime import datetime, timedelta
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            existing = db.query(PriceHistory).filter(
                PriceHistory.car_id == car.id,
                PriceHistory.recorded_at >= today_start
            ).first()
            
            if not existing:
                price_history = PriceHistory(car_id=car.id, price=car.price)
                db.add(price_history)
                db.commit()
                logger.info(f"[Alerts] Recorded price {car.price} for car {car.id} when alert was created")
    
    logger.info(f"[Alerts] Alert {alert.id} created successfully")
    return alert


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all alerts for current user"""
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id
    ).order_by(Alert.created_at.desc()).all()
    
    return alerts


@router.get("/notifications", status_code=status.HTTP_200_OK)
def get_price_drop_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get price drop notifications for current user's alerts"""
    from app.models import PriceHistory
    from sqlalchemy import desc
    
    # Get all active price_drop alerts for this user
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.alert_type == "price_drop",
        Alert.is_active == True
    ).all()
    
    notifications = []
    
    for alert in alerts:
        if alert.car_id:
            # Alert for specific car
            car = db.query(Car).filter(Car.id == alert.car_id).first()
            if not car:
                logger.debug(f"[Notifications] Car {alert.car_id} not found for alert {alert.id}")
                continue
            
            # Get price when alert was created (before alert creation)
            price_at_alert = db.query(PriceHistory).filter(
                PriceHistory.car_id == car.id,
                PriceHistory.recorded_at < alert.created_at
            ).order_by(desc(PriceHistory.recorded_at)).first()
            
            # If no price history before alert, we can't determine if price dropped
            # This means alert was created but price wasn't recorded yet
            if not price_at_alert:
                logger.debug(f"[Notifications] No price history before alert {alert.id} creation for car {car.id}")
                # Try to get the most recent price history (might be after alert creation)
                recent_price = db.query(PriceHistory).filter(
                    PriceHistory.car_id == car.id
                ).order_by(desc(PriceHistory.recorded_at)).first()
                
                if recent_price:
                    # Use the most recent price as baseline (price when alert was likely created)
                    baseline_price = recent_price.price
                else:
                    # No price history at all - skip this alert
                    logger.debug(f"[Notifications] No price history for car {car.id}, skipping alert {alert.id}")
                    continue
            else:
                baseline_price = price_at_alert.price
            
            current_price = car.price
            
            logger.debug(f"[Notifications] Alert {alert.id} - Car {car.id}: Baseline=${baseline_price:,.0f}, Current=${current_price:,.0f}")
            
            # Check if price dropped (current price must be less than baseline)
            if current_price < baseline_price:
                drop_amount = baseline_price - current_price
                drop_percent = (drop_amount / baseline_price * 100) if baseline_price > 0 else 0
                
                logger.info(f"[Notifications] Price drop found for alert {alert.id}: ${baseline_price:,.0f} -> ${current_price:,.0f}")
                
                notifications.append({
                    "alert_id": alert.id,
                    "car_id": car.id,
                    "car_name": f"{car.year} {car.make} {car.model}",
                    "old_price": baseline_price,
                    "new_price": current_price,
                    "drop_amount": drop_amount,
                    "drop_percent": drop_percent,
                    "message": f"Price dropped: {car.year} {car.make} {car.model} - ${baseline_price:,.0f} → ${current_price:,.0f} (${drop_amount:,.0f} / {drop_percent:.1f}% off)"
                })
        else:
            # General alert (no car_id) - check all cars matching criteria
            query = db.query(Car).filter(Car.is_available == True)
            
            if alert.make:
                query = query.filter(Car.make == alert.make)
            if alert.model:
                query = query.filter(Car.model == alert.model)
            if alert.max_price:
                query = query.filter(Car.price <= alert.max_price)
            
            matching_cars = query.all()
            
            for car in matching_cars:
                # Get price when alert was created
                price_at_alert = db.query(PriceHistory).filter(
                    PriceHistory.car_id == car.id,
                    PriceHistory.recorded_at < alert.created_at
                ).order_by(desc(PriceHistory.recorded_at)).first()
                
                if price_at_alert:
                    baseline_price = price_at_alert.price
                    current_price = car.price
                    
                    if current_price < baseline_price:
                        drop_amount = baseline_price - current_price
                        drop_percent = (drop_amount / baseline_price * 100) if baseline_price > 0 else 0
                        
                        notifications.append({
                            "alert_id": alert.id,
                            "car_id": car.id,
                            "car_name": f"{car.year} {car.make} {car.model}",
                            "old_price": baseline_price,
                            "new_price": current_price,
                            "drop_amount": drop_amount,
                            "drop_percent": drop_percent,
                            "message": f"Price dropped: {car.year} {car.make} {car.model} - ${baseline_price:,.0f} → ${current_price:,.0f} (${drop_amount:,.0f} / {drop_percent:.1f}% off)"
                        })
    
    return {"notifications": notifications, "count": len(notifications)}


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    logger.info(f"[Alerts] Alert {alert_id} deleted by user {current_user.id}")
    return


@router.patch("/{alert_id}/toggle", response_model=AlertResponse)
def toggle_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Toggle alert active status"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.is_active = not alert.is_active
    db.commit()
    db.refresh(alert)
    
    logger.info(f"[Alerts] Alert {alert_id} toggled to {alert.is_active}")
    return alert


def check_favorited_cars_price_drops(db: Session):
    """Check price drops for favorited cars with alerts"""
    from app.models import PriceHistory
    from sqlalchemy import desc
    
    alerts = db.query(Alert).filter(
        Alert.alert_type == "price_drop",
        Alert.car_id.isnot(None),
        Alert.is_active == True
    ).all()
    
    matches = []
    for alert in alerts:
        car = db.query(Car).filter(Car.id == alert.car_id).first()
        if not car:
            continue
        
        price_record = db.query(PriceHistory).filter(
            PriceHistory.car_id == car.id,
            PriceHistory.recorded_at <= alert.created_at
        ).order_by(desc(PriceHistory.recorded_at)).first()
        
        if price_record and car.price < price_record.price:
            drop = price_record.price - car.price
            drop_percent = (drop / price_record.price * 100) if price_record.price > 0 else 0
            if drop_percent >= 1.0:
                matches.append({
                    "alert_id": alert.id,
                    "user_id": alert.user_id,
                    "car_id": car.id,
                    "message": f"Price drop: {car.make} {car.model} dropped ${drop:,.0f} ({drop_percent:.1f}%)"
                })
    
    return matches


def check_price_drop_alerts(db: Session):
    """Check for price drops on cars with alerts"""
    from app.models import PriceHistory
    from sqlalchemy import desc
    
    alerts = db.query(Alert).filter(
        Alert.alert_type == "price_drop",
        Alert.is_active == True
    ).all()
    
    matches = []
    for alert in alerts:
        if alert.car_id:
            car = db.query(Car).filter(Car.id == alert.car_id).first()
            if not car:
                continue
            
            price_record = db.query(PriceHistory).filter(
                PriceHistory.car_id == car.id,
                PriceHistory.recorded_at < alert.created_at
            ).order_by(desc(PriceHistory.recorded_at)).first()
            
            if price_record and car.price < price_record.price:
                drop = price_record.price - car.price
                matches.append({
                    "alert_id": alert.id,
                    "user_id": alert.user_id,
                    "car_id": car.id,
                    "message": f"Price drop: {car.make} {car.model} dropped ${drop:,.0f}"
                })
        else:
            query = db.query(Car).filter(Car.is_available == True)
            if alert.make:
                query = query.filter(Car.make == alert.make)
            if alert.model:
                query = query.filter(Car.model == alert.model)
            if alert.max_price:
                query = query.filter(Car.price <= alert.max_price)
            
            for car in query.all():
                matches.append({
                    "alert_id": alert.id,
                    "user_id": alert.user_id,
                    "car_id": car.id,
                    "message": f"Match: {car.make} {car.model} - ${car.price:,.0f}"
                })
    
    return matches


def check_new_listing_alerts(db: Session):
    """Check for new listings matching alert criteria"""
    logger.info("[Alert Agent] Checking new listing alerts...")
    
    # Get all active new_listing alerts
    alerts = db.query(Alert).filter(
        Alert.alert_type == "new_listing",
        Alert.is_active == True
    ).all()
    
    matches = []
    
    for alert in alerts:
        query = db.query(Car).filter(Car.is_available == True)
        
        # Only check cars created after alert was created
        if alert.created_at:
            query = query.filter(Car.created_at >= alert.created_at)
        
        if alert.make:
            query = query.filter(Car.make == alert.make)
        if alert.model:
            query = query.filter(Car.model == alert.model)
        if alert.max_price:
            query = query.filter(Car.price <= alert.max_price)
        if alert.min_year:
            query = query.filter(Car.year >= alert.min_year)
        if alert.max_mileage:
            query = query.filter(Car.mileage <= alert.max_mileage)
        if alert.fuel_type:
            query = query.filter(Car.fuel_type == alert.fuel_type)
        
        cars = query.all()
        
        for car in cars:
            matches.append({
                "alert_id": alert.id,
                "user_id": alert.user_id,
                "car_id": car.id,
                "message": f"New listing alert: {car.make} {car.model} - ${car.price:,.0f}"
            })
    
    logger.info(f"[Alert Agent] Found {len(matches)} new listing matches")
    return matches


@router.post("/check", status_code=status.HTTP_200_OK)
def check_alerts(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger alert checking (for testing or scheduled tasks)
    In production, this would be called by a cron job or task scheduler
    """
    logger.info("[Alerts] Manual alert check triggered")
    
    # Run checks in background
    price_matches = check_price_drop_alerts(db)
    listing_matches = check_new_listing_alerts(db)
    
    return {
        "price_drop_matches": len(price_matches),
        "new_listing_matches": len(listing_matches),
        "total_matches": len(price_matches) + len(listing_matches),
        "matches": price_matches + listing_matches
    }


# Background task function (can be called by scheduler)
def run_alert_agent(db: Session):
    """Run the alert agent"""
    price_matches = check_price_drop_alerts(db)
    favorite_matches = check_favorited_cars_price_drops(db)
    listing_matches = check_new_listing_alerts(db)
    
    all_matches = price_matches + favorite_matches + listing_matches
    
    return {
        "status": "completed",
        "matches_found": len(all_matches),
        "matches": all_matches
    }

