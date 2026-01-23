"""
Predictions API endpoints for ownership cost and future value
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Car, CarSpec
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class OwnershipCostResponse(BaseModel):
    """Response for ownership cost prediction"""
    car_id: int
    purchase_price: float
    years: int
    annual_mileage: int
    
    # Cost breakdown
    depreciation: float
    fuel_cost: float
    insurance: float
    maintenance: float
    repairs: float
    registration_taxes: float
    
    # Totals
    total_cost: float
    monthly_cost: float
    cost_per_mile: float
    
    # Breakdown by year
    yearly_breakdown: list


class FutureValueResponse(BaseModel):
    """Response for future value prediction"""
    car_id: int
    current_price: float
    current_year: int
    current_mileage: int
    
    # Predictions
    predictions: list  # List of {year: int, value: float, mileage: int, depreciation_rate: float}


def calculate_depreciation_rate(car: Car) -> float:
    """
    Calculate depreciation rate based on car make and age
    Higher-end brands depreciate slower, older cars depreciate slower
    """
    # Base depreciation rate (percentage per year)
    base_rate = 0.15  # 15% per year average
    
    # Adjust based on make (luxury brands depreciate slower)
    luxury_brands = ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 'Porsche', 'Tesla']
    if car.make in luxury_brands:
        base_rate = 0.12  # 12% for luxury
    
    # Adjust based on age (newer cars depreciate faster)
    car_age = datetime.now().year - car.year
    if car_age <= 1:
        base_rate = 0.20  # 20% for brand new
    elif car_age <= 3:
        base_rate = 0.15  # 15% for 2-3 years
    elif car_age <= 5:
        base_rate = 0.12  # 12% for 4-5 years
    else:
        base_rate = 0.08  # 8% for older cars
    
    # Adjust based on condition
    if car.condition == 'excellent':
        base_rate *= 0.9
    elif car.condition == 'fair':
        base_rate *= 1.1
    
    return base_rate


def calculate_fuel_cost(car: Car, annual_mileage: int, years: int) -> float:
    """Calculate total fuel cost over ownership period"""
    if not car.specs:
        # Default estimates if no specs
        if car.fuel_type == 'electric':
            # Electric: $0.12 per kWh, assume 3.5 miles per kWh
            cost_per_mile = 0.12 / 3.5
        elif car.fuel_type == 'hybrid':
            # Hybrid: 50 MPG average, $3.50/gallon
            cost_per_mile = 3.50 / 50
        else:
            # Gasoline: 25 MPG average, $3.50/gallon
            cost_per_mile = 3.50 / 25
    else:
        specs = car.specs
        if car.fuel_type == 'electric':
            cost_per_mile = 0.12 / 3.5  # $0.12/kWh, 3.5 mi/kWh
        elif specs.mpg_highway and specs.mpg_city:
            avg_mpg = (specs.mpg_city + specs.mpg_highway) / 2
            fuel_price = 3.50  # $3.50 per gallon average
            cost_per_mile = fuel_price / avg_mpg
        else:
            cost_per_mile = 3.50 / 25  # Default
    
    total_miles = annual_mileage * years
    return cost_per_mile * total_miles


def calculate_insurance(car: Car, years: int) -> float:
    """Calculate insurance cost (varies by car value and type)"""
    # Base insurance: 3-5% of car value per year
    base_rate = 0.04  # 4% per year
    
    # Adjust for make (luxury = higher insurance)
    luxury_brands = ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 'Porsche']
    if car.make in luxury_brands:
        base_rate = 0.06  # 6% for luxury
    
    # Adjust for age (newer = higher insurance)
    car_age = datetime.now().year - car.year
    if car_age <= 3:
        base_rate *= 1.2
    
    annual_insurance = car.price * base_rate
    return annual_insurance * years


def calculate_maintenance(car: Car, annual_mileage: int, years: int) -> float:
    """Calculate maintenance cost"""
    # Average maintenance: $0.10-0.15 per mile
    cost_per_mile = 0.12
    
    # Electric cars have lower maintenance
    if car.fuel_type == 'electric':
        cost_per_mile = 0.06
    
    total_miles = annual_mileage * years
    return cost_per_mile * total_miles


def calculate_repairs(car: Car, years: int) -> float:
    """Calculate expected repair costs"""
    # Repairs increase with age
    car_age = datetime.now().year - car.year
    base_repair_cost = car.price * 0.02  # 2% per year base
    
    # Higher for older cars
    if car_age + years > 10:
        base_repair_cost *= 1.5
    
    # Lower for reliable brands
    reliable_brands = ['Toyota', 'Honda', 'Lexus']
    if car.make in reliable_brands:
        base_repair_cost *= 0.7
    
    return base_repair_cost * years


@router.get("/cars/{car_id}/ownership-cost", response_model=OwnershipCostResponse)
def get_ownership_cost(
    car_id: int,
    years: int = Query(5, ge=1, le=10, description="Years of ownership"),
    annual_mileage: int = Query(12000, ge=1000, le=50000, description="Annual mileage"),
    db: Session = Depends(get_db)
):
    """
    Calculate total ownership cost for a car over specified years
    """
    logger.info(f"[Predictions] Calculating ownership cost for car {car_id}, {years} years, {annual_mileage} miles/year")
    
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    purchase_price = car.price
    
    # Calculate depreciation
    depreciation_rate = calculate_depreciation_rate(car)
    depreciation = purchase_price * (1 - (1 - depreciation_rate) ** years)
    
    # Calculate fuel cost
    fuel_cost = calculate_fuel_cost(car, annual_mileage, years)
    
    # Calculate insurance
    insurance = calculate_insurance(car, years)
    
    # Calculate maintenance
    maintenance = calculate_maintenance(car, annual_mileage, years)
    
    # Calculate repairs
    repairs = calculate_repairs(car, years)
    
    # Registration and taxes (estimate $500/year)
    registration_taxes = 500 * years
    
    # Total cost
    total_cost = depreciation + fuel_cost + insurance + maintenance + repairs + registration_taxes
    
    # Monthly cost
    monthly_cost = total_cost / (years * 12)
    
    # Cost per mile
    total_miles = annual_mileage * years
    cost_per_mile = total_cost / total_miles if total_miles > 0 else 0
    
    # Yearly breakdown
    yearly_breakdown = []
    remaining_value = purchase_price
    
    for year in range(1, years + 1):
        year_depreciation = remaining_value * depreciation_rate
        remaining_value -= year_depreciation
        
        year_fuel = calculate_fuel_cost(car, annual_mileage, 1)
        year_insurance = calculate_insurance(car, 1)
        year_maintenance = calculate_maintenance(car, annual_mileage, 1)
        year_repairs = calculate_repairs(car, 1) / years  # Average per year
        year_registration = 500
        
        year_total = year_depreciation + year_fuel + year_insurance + year_maintenance + year_repairs + year_registration
        
        yearly_breakdown.append({
            "year": year,
            "depreciation": round(year_depreciation, 2),
            "fuel": round(year_fuel, 2),
            "insurance": round(year_insurance, 2),
            "maintenance": round(year_maintenance, 2),
            "repairs": round(year_repairs, 2),
            "registration": year_registration,
            "total": round(year_total, 2),
            "remaining_value": round(remaining_value, 2)
        })
    
    return OwnershipCostResponse(
        car_id=car_id,
        purchase_price=purchase_price,
        years=years,
        annual_mileage=annual_mileage,
        depreciation=round(depreciation, 2),
        fuel_cost=round(fuel_cost, 2),
        insurance=round(insurance, 2),
        maintenance=round(maintenance, 2),
        repairs=round(repairs, 2),
        registration_taxes=registration_taxes,
        total_cost=round(total_cost, 2),
        monthly_cost=round(monthly_cost, 2),
        cost_per_mile=round(cost_per_mile, 2),
        yearly_breakdown=yearly_breakdown
    )


@router.get("/cars/{car_id}/future-value", response_model=FutureValueResponse)
def get_future_value(
    car_id: int,
    years_ahead: int = Query(5, ge=1, le=10, description="Years to predict ahead"),
    db: Session = Depends(get_db)
):
    """
    Predict future value of a car using depreciation logic
    """
    logger.info(f"[Predictions] Predicting future value for car {car_id}, {years_ahead} years ahead")
    
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    current_price = car.price
    current_year = datetime.now().year
    current_mileage = car.mileage
    
    # Calculate depreciation rate
    depreciation_rate = calculate_depreciation_rate(car)
    
    # Estimate annual mileage (12,000 miles/year average)
    annual_mileage = 12000
    
    predictions = []
    remaining_value = current_price
    predicted_mileage = current_mileage
    
    for year in range(1, years_ahead + 1):
        # Apply depreciation
        year_depreciation = remaining_value * depreciation_rate
        remaining_value -= year_depreciation
        
        # Update mileage
        predicted_mileage += annual_mileage
        
        # Mileage affects value (every 10,000 miles = ~2% value reduction)
        mileage_penalty = (predicted_mileage - current_mileage) / 10000 * 0.02
        remaining_value *= (1 - mileage_penalty)
        
        predictions.append({
            "year": current_year + year,
            "value": round(remaining_value, 2),
            "mileage": int(predicted_mileage),
            "depreciation_rate": round(depreciation_rate * 100, 1),
            "total_depreciation": round(current_price - remaining_value, 2),
            "depreciation_percentage": round(((current_price - remaining_value) / current_price) * 100, 1)
        })
    
    return FutureValueResponse(
        car_id=car_id,
        current_price=current_price,
        current_year=current_year,
        current_mileage=current_mileage,
        predictions=predictions
    )


class CarValueEstimateRequest(BaseModel):
    """Request for car value estimation"""
    make: str
    model: str
    year: int
    mileage: int
    condition: str  # new, excellent, good, fair, poor
    original_price: Optional[float] = None  # Optional: if user knows original price
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None


class CarValueEstimateResponse(BaseModel):
    """Response for car value estimation"""
    estimated_value: float
    value_range: dict  # {min: float, max: float}
    factors: dict  # Factors affecting the value
    depreciation_amount: Optional[float] = None
    depreciation_percentage: Optional[float] = None


def estimate_car_value(
    make: str,
    model: str,
    year: int,
    mileage: int,
    condition: str,
    original_price: Optional[float] = None,
    fuel_type: Optional[str] = None,
    transmission: Optional[str] = None,
    db: Session = None
) -> dict:
    """
    Estimate current market value of a car based on its details
    
    Logic:
    1. If original_price provided: Calculate depreciation from original
    2. If not: Find similar cars in database and estimate from their prices
    3. Adjust for mileage, condition, age
    """
    current_year = datetime.now().year
    car_age = current_year - year
    
    # Step 1: Get base value
    if original_price:
        # User provided original price - calculate from that
        base_value = original_price
        has_original_price = True
    else:
        # Try to find similar cars in database to estimate base value
        if db:
            similar_cars = db.query(Car).filter(
                Car.make == make,
                Car.model == model,
                Car.year == year,
                Car.is_available == True
            ).all()
            
            if similar_cars:
                # Average price of similar cars
                avg_price = sum(car.price for car in similar_cars) / len(similar_cars)
                base_value = avg_price
                has_original_price = False
            else:
                # No similar cars found - estimate based on make/model/year
                # This is a rough estimate - in production, you'd use a pricing API
                base_value = estimate_base_value_from_make_model(make, model, year)
                has_original_price = False
        else:
            base_value = estimate_base_value_from_make_model(make, model, year)
            has_original_price = False
    
    # Step 2: Calculate depreciation based on age
    depreciation_rate = calculate_depreciation_rate_from_age(car_age, make)
    
    # Apply depreciation
    if has_original_price:
        # Calculate how much value has been lost
        years_depreciation = (1 - depreciation_rate) ** car_age
        estimated_value = base_value * years_depreciation
        depreciation_amount = base_value - estimated_value
        depreciation_percentage = (depreciation_amount / base_value) * 100 if base_value > 0 else 0
    else:
        # Base value is already current market price, just adjust for condition/mileage
        estimated_value = base_value
        depreciation_amount = None
        depreciation_percentage = None
    
    # Step 3: Adjust for mileage
    # Average mileage per year: 12,000 miles
    expected_mileage = car_age * 12000
    mileage_difference = mileage - expected_mileage
    
    # Every 10,000 miles above/below expected = 2% value change
    mileage_adjustment = (mileage_difference / 10000) * 0.02
    estimated_value *= (1 - mileage_adjustment)
    
    # Step 4: Adjust for condition
    condition_multipliers = {
        'new': 1.0,
        'excellent': 0.95,
        'good': 0.90,
        'fair': 0.80,
        'poor': 0.65
    }
    condition_multiplier = condition_multipliers.get(condition.lower(), 0.90)
    estimated_value *= condition_multiplier
    
    # Step 5: Calculate value range (±10%)
    value_min = estimated_value * 0.90
    value_max = estimated_value * 1.10
    
    # Step 6: Prepare factors
    factors = {
        'age_years': car_age,
        'depreciation_rate': round(depreciation_rate * 100, 1),
        'mileage_adjustment': round(mileage_adjustment * 100, 2),
        'condition_adjustment': round((1 - condition_multiplier) * 100, 1),
        'expected_mileage': expected_mileage,
        'mileage_difference': mileage_difference
    }
    
    return {
        'estimated_value': round(estimated_value, 2),
        'value_range': {
            'min': round(value_min, 2),
            'max': round(value_max, 2)
        },
        'factors': factors,
        'depreciation_amount': round(depreciation_amount, 2) if depreciation_amount else None,
        'depreciation_percentage': round(depreciation_percentage, 1) if depreciation_percentage else None
    }


def calculate_depreciation_rate_from_age(car_age: int, make: str) -> float:
    """Calculate depreciation rate based on car age and make"""
    # Luxury brands depreciate slower
    luxury_brands = ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 'Porsche', 'Tesla']
    
    if car_age <= 1:
        base_rate = 0.20  # 20% for brand new
    elif car_age <= 3:
        base_rate = 0.15  # 15% for 2-3 years
    elif car_age <= 5:
        base_rate = 0.12  # 12% for 4-5 years
    else:
        base_rate = 0.08  # 8% for older cars
    
    if make in luxury_brands:
        base_rate *= 0.8  # Luxury depreciates 20% slower
    
    return base_rate


def estimate_base_value_from_make_model(make: str, model: str, year: int) -> float:
    """
    Rough estimate of base value when no database match found
    This is a fallback - in production, use a pricing API like KBB, Edmunds, etc.
    """
    # Very rough estimates based on typical car prices
    # In production, you'd call an external pricing API
    
    base_prices = {
        'Toyota': {'Camry': 28000, 'Corolla': 22000, 'RAV4': 32000},
        'Honda': {'Civic': 24000, 'Accord': 28000, 'CR-V': 30000},
        'BMW': {'3 Series': 45000, '5 Series': 55000, 'X3': 45000},
        'Mercedes-Benz': {'C-Class': 45000, 'E-Class': 55000, 'GLC': 45000},
        'Ford': {'F-150': 40000, 'Mustang': 35000, 'Explorer': 35000},
        'Kia': {'Forte': 20000, 'Optima': 25000, 'Sorento': 30000}
    }
    
    if make in base_prices and model in base_prices[make]:
        base_price = base_prices[make][model]
    else:
        base_price = 30000  # Default estimate
    
    # Adjust for year
    from datetime import datetime
    current_year = datetime.now().year
    age = current_year - year
    
    # Apply some depreciation for age
    if age > 0:
        depreciation = (1 - 0.15) ** age
        base_price = base_price * depreciation
    
    return base_price


@router.post("/estimate-value", response_model=CarValueEstimateResponse, status_code=status.HTTP_200_OK)
def estimate_my_car_value(
    car_data: CarValueEstimateRequest,
    db: Session = Depends(get_db)
):
    """
    Estimate current market value of a user's car
    
    User provides:
    - make, model, year
    - current mileage
    - condition
    - optional: original purchase price
    
    Returns estimated current market value
    """
    logger.info(f"[Car Value] Estimating value for {car_data.year} {car_data.make} {car_data.model}")
    
    result = estimate_car_value(
        make=car_data.make,
        model=car_data.model,
        year=car_data.year,
        mileage=car_data.mileage,
        condition=car_data.condition,
        original_price=car_data.original_price,
        fuel_type=car_data.fuel_type,
        transmission=car_data.transmission,
        db=db
    )
    
    logger.info(f"[Car Value] Estimated value: ${result['estimated_value']:,.2f}")
    
    return CarValueEstimateResponse(**result)

