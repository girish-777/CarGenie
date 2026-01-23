"""
Simple script to sync database cars with available images
Only keeps cars that match the 10 images in frontend/images/
"""
import sys
import os

# Add backend to path (go up one level from db_deploy to project root, then into backend)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.db.database import SessionLocal
from app.models import Car

def sync_cars_to_images():
    """Keep only cars that match available images"""
    db = SessionLocal()
    try:
        # Define cars that match the 10 images
        matching_cars = [
            {'year': 2023, 'make': 'Toyota', 'model': 'Camry'},
            {'year': 2024, 'make': 'BMW', 'model': 'i4'},
            {'year': 2024, 'make': 'Ford', 'model': 'F-150 Lightning'},
            {'year': 2024, 'make': 'Ford', 'model': 'F-150'},
            {'year': 2024, 'make': 'Kia', 'model': 'EV6'},
            {'year': 2024, 'make': 'Kia', 'model': 'Sportage'},
            {'year': 2024, 'make': 'Mercedes-Benz', 'model': 'C-Class'},
            {'year': 2024, 'make': 'Mercedes-Benz', 'model': 'EQS'},
            {'year': 2024, 'make': 'Toyota', 'model': 'bZ4X'},
            {'year': 2023, 'make': 'BMW', 'model': '3 Series'},  # BMW 3 Series.jpg (no year prefix)
        ]
        
        # Get all existing cars
        all_cars = db.query(Car).all()
        
        cars_to_keep = []
        cars_to_delete = []
        
        # Check each existing car
        for car in all_cars:
            # Check if car matches any of our target cars
            matches = False
            for target in matching_cars:
                if (car.year == target['year'] and 
                    car.make == target['make'] and 
                    car.model == target['model']):
                    matches = True
                    cars_to_keep.append(car)
                    break
            
            if not matches:
                cars_to_delete.append(car)
        
        print(f"Cars to keep: {len(cars_to_keep)}")
        for car in cars_to_keep:
            print(f"  - {car.year} {car.make} {car.model} (ID: {car.id})")
        
        print(f"\nCars to delete: {len(cars_to_delete)}")
        for car in cars_to_delete:
            print(f"  - {car.year} {car.make} {car.model} (ID: {car.id})")
        
        # Delete cars that don't match
        for car in cars_to_delete:
            db.delete(car)
            print(f"[DELETE] Removed {car.year} {car.make} {car.model}")
        
        # Create missing cars
        existing_car_keys = {(c.year, c.make, c.model) for c in cars_to_keep}
        
        for target in matching_cars:
            key = (target['year'], target['make'], target['model'])
            if key not in existing_car_keys:
                # Create new car with default values
                new_car = Car(
                    year=target['year'],
                    make=target['make'],
                    model=target['model'],
                    price=35000.0,  # Default price
                    mileage=0,
                    fuel_type='Gasoline',  # Required field
                    transmission='Automatic',  # Default
                    color='White',  # Default
                    condition='Excellent',  # Default
                    engine_condition='Excellent',  # Default
                    location='Available',  # Default
                    description=f'{target["year"]} {target["make"]} {target["model"]}',  # Default
                    image_urls=[],  # Will be set by assign_car_images.py
                    is_available=True,
                )
                db.add(new_car)
                print(f"[CREATE] Added {target['year']} {target['make']} {target['model']}")
        
        db.commit()
        print(f"\n[SUCCESS] Database synced with images!")
        print(f"Total cars now: {db.query(Car).count()}")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Syncing Database Cars with Available Images")
    print("=" * 60)
    print()
    sync_cars_to_images()
    print()
    print("=" * 60)
    print("Done! Now run: python assign_car_images.py")
    print("=" * 60)

