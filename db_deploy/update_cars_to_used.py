"""
Update all cars to be used cars with realistic mileage
"""
import sys
import os

# Add backend directory to path (go up one level from db_deploy to project root, then into backend)
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.car import Car
import random
from datetime import datetime

def update_cars_to_used():
    """Update all cars to be used with realistic mileage based on year"""
    db: Session = SessionLocal()
    
    try:
        cars = db.query(Car).all()
        print(f"Found {len(cars)} cars to update")
        
        current_year = datetime.now().year
        
        for car in cars:
            # Calculate age of car
            age = current_year - car.year
            
            # Calculate realistic mileage based on age
            # Average 12,000-15,000 miles per year
            base_miles_per_year = random.randint(12000, 15000)
            mileage = base_miles_per_year * age
            
            # Add some variation (±20%)
            variation = random.randint(-20, 20)
            mileage = int(mileage * (1 + variation / 100))
            
            # Ensure minimum mileage for used cars (at least 5,000 miles)
            mileage = max(5000, mileage)
            
            # Update condition to "used"
            car.condition = "used"
            car.mileage = mileage
            
            # Set engine condition if not set or if it's capitalized
            if not car.engine_condition or car.engine_condition.lower() != car.engine_condition:
                # Randomly assign engine condition based on mileage
                if mileage < 30000:
                    car.engine_condition = random.choice(["excellent", "excellent", "good"])
                elif mileage < 60000:
                    car.engine_condition = random.choice(["excellent", "good", "good"])
                else:
                    car.engine_condition = random.choice(["good", "good", "fair"])
            else:
                # Ensure lowercase
                car.engine_condition = car.engine_condition.lower()
            
            print(f"Updated {car.year} {car.make} {car.model}: {car.mileage:,} miles, {car.condition}, engine: {car.engine_condition}")
        
        db.commit()
        print(f"\nSuccessfully updated {len(cars)} cars to used with realistic mileage")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating cars: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_cars_to_used()

