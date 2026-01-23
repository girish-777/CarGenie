"""
Database seeding script for Day 2
Populates database with sample car data and creates admin user
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db.database import SessionLocal
from app.models import User, Car, CarSpec, CarScore
from app.core.security import get_password_hash

# Sample car data
SAMPLE_CARS = [
    {
        "make": "Toyota",
        "model": "Camry",
        "year": 2023,
        "price": 27075.00,  # Base: 28500, Excellent: 95%
        "mileage": 15000,
        "fuel_type": "hybrid",
        "transmission": "automatic",
        "color": "Silver",
        "condition": "used",
        "engine_condition": "excellent",
        "location": "Los Angeles, CA",
        "description": "Well-maintained 2023 Toyota Camry Hybrid with excellent fuel economy. Engine in excellent condition - runs smoothly, no issues. One owner, clean CarFax. Perfect for daily commuting.",
        "image_urls": ["images/2023-Toyota-Camry.webp"],
        "vin": "4T1B11HK5JU123456",
        "specs": {
            "engine_size": 2.5,
            "cylinders": 4,
            "horsepower": 208,
            "torque": 163,
            "acceleration_0_60": 7.8,
            "top_speed": 120,
            "mpg_city": 51,
            "mpg_highway": 53,
            "length": 192.1,
            "width": 72.4,
            "height": 56.9,
            "weight": 3580,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "FWD"
        },
        "scores": {
            "reliability_score": 9.2,
            "safety_score": 9.5,
            "overall_score": 9.3,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 9.0
        }
    },
    {
        "make": "Honda",
        "model": "Civic",
        "year": 2022,
        "price": 22050.00,  # Base: 24500, Good: 90%
        "mileage": 22000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "Blue",
        "condition": "used",
        "engine_condition": "good",
        "location": "San Francisco, CA",
        "description": "2022 Honda Civic with modern features and great reliability. Engine in good condition - well-maintained, regularly serviced. Normal wear for age and mileage.",
        "image_urls": ["images/2023-Toyota-Camry.webp"],  # Using available image
        "vin": "19XFC2F59NE234567",
        "specs": {
            "engine_size": 2.0,
            "cylinders": 4,
            "horsepower": 158,
            "torque": 138,
            "acceleration_0_60": 8.2,
            "top_speed": 125,
            "mpg_city": 31,
            "mpg_highway": 40,
            "length": 182.7,
            "width": 70.9,
            "height": 55.7,
            "weight": 2877,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "FWD"
        },
        "scores": {
            "reliability_score": 9.0,
            "safety_score": 9.3,
            "overall_score": 9.1,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 8.8
        }
    },
    {
        "make": "Tesla",
        "model": "Model 3",
        "year": 2023,
        "price": 38022.00,  # Base: 38900, Excellent: 97.75%
        "mileage": 5000,
        "fuel_type": "electric",
        "transmission": "automatic",
        "color": "White",
        "condition": "used",
        "engine_condition": "excellent",
        "location": "Seattle, WA",
        "description": "2023 Tesla Model 3 with Autopilot. Low mileage, like new condition. Electric motor in excellent condition - virtually no wear. Full warranty remaining.",
        "image_urls": ["images/2024 Kia EV6.jpg"],  # Using available EV image
        "vin": "5YJ3E1EB8KF345678",
        "specs": {
            "engine_size": 0.0,  # Electric
            "cylinders": 0,
            "horsepower": 283,
            "torque": 307,
            "acceleration_0_60": 5.3,
            "top_speed": 140,
            "mpg_city": 132,  # MPGe
            "mpg_highway": 126,
            "length": 184.8,
            "width": 72.8,
            "height": 56.8,
            "weight": 3549,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "RWD"
        },
        "scores": {
            "reliability_score": 8.5,
            "safety_score": 9.8,
            "overall_score": 9.1,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 8.0
        }
    },
    {
        "make": "Ford",
        "model": "F-150",
        "year": 2022,
        "price": 37800.00,  # Base: 42000, Good: 90%
        "mileage": 18000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "Black",
        "condition": "used",
        "engine_condition": "good",
        "location": "Dallas, TX",
        "description": "2022 Ford F-150 XLT with towing package. Engine in good condition - strong performance, well-maintained. Perfect for work or recreation.",
        "image_urls": ["images/2024 Ford F-150.jpg"],
        "vin": "1FTFW1E58NFC456789",
        "specs": {
            "engine_size": 3.5,
            "cylinders": 6,
            "horsepower": 400,
            "torque": 500,
            "acceleration_0_60": 6.5,
            "top_speed": 110,
            "mpg_city": 18,
            "mpg_highway": 24,
            "length": 231.9,
            "width": 79.9,
            "height": 77.2,
            "weight": 4521,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "4WD"
        },
        "scores": {
            "reliability_score": 8.8,
            "safety_score": 9.0,
            "overall_score": 8.9,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 8.5
        }
    },
    {
        "make": "BMW",
        "model": "3 Series",
        "year": 2023,
        "price": 38610.00,  # Base: 42900, Good: 90%
        "mileage": 8000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "Gray",
        "condition": "used",
        "engine_condition": "good",
        "location": "New York, NY",
        "description": "2023 BMW 3 Series with premium package. Engine in good condition - runs well, properly maintained. Used vehicle with low mileage.",
        "image_urls": ["images/BMW 3 Series.jpg"],
        "vin": "WBA8A9C58ED567890",
        "specs": {
            "engine_size": 2.0,
            "cylinders": 4,
            "horsepower": 255,
            "torque": 295,
            "acceleration_0_60": 5.6,
            "top_speed": 155,
            "mpg_city": 26,
            "mpg_highway": 36,
            "length": 185.7,
            "width": 71.9,
            "height": 56.8,
            "weight": 3582,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "RWD"
        },
        "scores": {
            "reliability_score": 8.0,
            "safety_score": 9.2,
            "overall_score": 8.6,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 7.5
        }
    },
    {
        "make": "Mercedes-Benz",
        "model": "C-Class",
        "year": 2022,
        "price": 35010.00,  # Base: 38900, Good: 90%
        "mileage": 25000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "Silver",
        "condition": "used",
        "engine_condition": "good",
        "location": "Miami, FL",
        "description": "2022 Mercedes-Benz C-Class with luxury features. Engine in good condition - smooth operation, well-maintained. Single owner.",
        "image_urls": ["images/2024 Mercedes-Benz C-Class.jpg"],
        "vin": "WDDWF4KB5NR678901",
        "specs": {
            "engine_size": 2.0,
            "cylinders": 4,
            "horsepower": 255,
            "torque": 273,
            "acceleration_0_60": 6.0,
            "top_speed": 130,
            "mpg_city": 24,
            "mpg_highway": 35,
            "length": 184.5,
            "width": 71.3,
            "height": 56.8,
            "weight": 3616,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "RWD"
        },
        "scores": {
            "reliability_score": 8.2,
            "safety_score": 9.4,
            "overall_score": 8.8,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 7.8
        }
    },
    {
        "make": "Audi",
        "model": "A4",
        "year": 2023,
        "price": 40595.00,  # Base: 41900, Excellent: 96.9%
        "mileage": 12000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "Black",
        "condition": "used",
        "engine_condition": "excellent",
        "location": "Chicago, IL",
        "description": "2023 Audi A4 with premium features. Engine in excellent condition - like new, low mileage. Excellent overall condition.",
        "image_urls": ["images/2024 Mercedes-Benz C-Class.jpg"],  # Using available luxury car image
        "vin": "WAUAF2AF8DN789012",
        "specs": {
            "engine_size": 2.0,
            "cylinders": 4,
            "horsepower": 261,
            "torque": 273,
            "acceleration_0_60": 5.7,
            "top_speed": 130,
            "mpg_city": 25,
            "mpg_highway": 34,
            "length": 187.5,
            "width": 72.7,
            "height": 56.2,
            "weight": 3616,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "AWD"
        },
        "scores": {
            "reliability_score": 8.3,
            "safety_score": 9.3,
            "overall_score": 8.8,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 7.9
        }
    },
    {
        "make": "Nissan",
        "model": "Altima",
        "year": 2022,
        "price": 18320.00,  # Base: 22900, Fair: 80%
        "mileage": 30000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "Red",
        "condition": "used",
        "engine_condition": "fair",
        "location": "Phoenix, AZ",
        "description": "2022 Nissan Altima with higher mileage. Engine in fair condition - functional but shows some wear. Reliable daily driver.",
        "image_urls": ["images/2024 Kia Sportage.jpg"],  # Using available sedan image
        "vin": "1N4BL4CV9NC890123",
        "specs": {
            "engine_size": 2.5,
            "cylinders": 4,
            "horsepower": 188,
            "torque": 180,
            "acceleration_0_60": 8.5,
            "top_speed": 120,
            "mpg_city": 28,
            "mpg_highway": 39,
            "length": 192.9,
            "width": 72.9,
            "height": 57.4,
            "weight": 3230,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "FWD"
        },
        "scores": {
            "reliability_score": 8.5,
            "safety_score": 9.0,
            "overall_score": 8.7,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 8.2
        }
    },
    {
        "make": "Chevrolet",
        "model": "Silverado",
        "year": 2022,
        "price": 30400.00,  # Base: 38000, Fair: 80%
        "mileage": 20000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "White",
        "condition": "used",
        "engine_condition": "fair",
        "location": "Houston, TX",
        "description": "2022 Chevrolet Silverado 1500. Engine in fair condition - works well but shows typical wear. Great for towing and hauling.",
        "image_urls": ["images/2024 Ford F-150 Lightning.jpg"],  # Using available truck image
        "vin": "1GCVKREC2NZ901234",
        "specs": {
            "engine_size": 5.3,
            "cylinders": 8,
            "horsepower": 355,
            "torque": 383,
            "acceleration_0_60": 7.0,
            "top_speed": 112,
            "mpg_city": 16,
            "mpg_highway": 20,
            "length": 230.0,
            "width": 81.2,
            "height": 75.6,
            "weight": 4800,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "4WD"
        },
        "scores": {
            "reliability_score": 8.6,
            "safety_score": 8.9,
            "overall_score": 8.7,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 8.3
        }
    },
    {
        "make": "Hyundai",
        "model": "Elantra",
        "year": 2023,
        "price": 21243.00,  # Base: 21900, Excellent: 97%
        "mileage": 10000,
        "fuel_type": "gasoline",
        "transmission": "automatic",
        "color": "Blue",
        "condition": "used",
        "engine_condition": "excellent",
        "location": "Atlanta, GA",
        "description": "2023 Hyundai Elantra with modern tech features. Engine in excellent condition - very low mileage, runs perfectly. Excellent warranty remaining.",
        "image_urls": ["images/2023-Toyota-Camry.webp"],  # Using available sedan image
        "vin": "5NPE34AF8PH012345",
        "specs": {
            "engine_size": 2.0,
            "cylinders": 4,
            "horsepower": 147,
            "torque": 132,
            "acceleration_0_60": 8.8,
            "top_speed": 118,
            "mpg_city": 31,
            "mpg_highway": 41,
            "length": 184.1,
            "width": 71.9,
            "height": 55.7,
            "weight": 2858,
            "seating_capacity": 5,
            "doors": 4,
            "drivetrain": "FWD"
        },
        "scores": {
            "reliability_score": 8.7,
            "safety_score": 9.1,
            "overall_score": 8.9,
            "crash_test_rating": "5-Star NHTSA",
            "predicted_reliability": 8.4
        }
    }
]


def create_admin_user(db):
    """Create admin user if it doesn't exist"""
    admin_email = "admin@cargenie.com"
    admin_password = "admin123"  # Change in production!
    
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if existing_admin:
        print(f"Admin user '{admin_email}' already exists. Skipping...")
        return existing_admin
    
    # Hash password using the same method as the application
    hashed = get_password_hash(admin_password)
    admin_user = User(
        email=admin_email,
        hashed_password=hashed,
        full_name="Admin User",
        is_active=True,
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print(f"[OK] Created admin user: {admin_email} (password: {admin_password})")
    return admin_user


def seed_cars(db):
    """Seed database with sample car data - Only 10 cars"""
    cars_created = 0
    
    # Ensure we only seed exactly 10 cars
    cars_to_seed = SAMPLE_CARS[:10]
    print(f"Seeding exactly {len(cars_to_seed)} cars...")
    
    # Get VINs of cars we want to keep
    keep_vins = {car_data.get("vin") for car_data in cars_to_seed if car_data.get("vin")}
    
    # Remove any cars not in our list (to ensure only 10 cars)
    all_cars = db.query(Car).all()
    for car in all_cars:
        if car.vin not in keep_vins:
            print(f"Removing car not in list: {car.year} {car.make} {car.model} (VIN: {car.vin})")
            db.delete(car)
    db.commit()
    
    for car_data in cars_to_seed:
        # Check if car already exists (by VIN)
        existing_car = None
        if car_data.get("vin"):
            existing_car = db.query(Car).filter(Car.vin == car_data["vin"]).first()
        
        # Extract specs and scores before modifying car_data
        specs_data = car_data.pop("specs", {})
        scores_data = car_data.pop("scores", {})
        
        if existing_car:
            # Update existing car
            print(f"Car {car_data['make']} {car_data['model']} ({car_data['vin']}) already exists. Updating...")
            for key, value in car_data.items():
                if hasattr(existing_car, key):
                    setattr(existing_car, key, value)
            car = existing_car
            db.flush()
        else:
            # Create new car
            car = Car(**car_data)
            db.add(car)
            db.flush()  # Get the car ID
            cars_created += 1
            print(f"[OK] Created: {car.year} {car.make} {car.model} - ${car.price:,.0f}")
        
        # Update or create car specs
        if specs_data:
            existing_spec = db.query(CarSpec).filter(CarSpec.car_id == car.id).first()
            if existing_spec:
                for key, value in specs_data.items():
                    if hasattr(existing_spec, key):
                        setattr(existing_spec, key, value)
            else:
                car_spec = CarSpec(car_id=car.id, **specs_data)
                db.add(car_spec)
        
        # Update or create car scores
        if scores_data:
            existing_score = db.query(CarScore).filter(CarScore.car_id == car.id).first()
            if existing_score:
                for key, value in scores_data.items():
                    if hasattr(existing_score, key):
                        setattr(existing_score, key, value)
            else:
                car_score = CarScore(car_id=car.id, **scores_data)
                db.add(car_score)
    
    db.commit()
    final_count = db.query(Car).count()
    print(f"Total cars in database: {final_count} (should be 10)")
    return cars_created


def main():
    """Main seeding function"""
    print("=" * 60)
    print("Database Seeding Script - Day 2")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    
    try:
        # Create admin user
        print("Creating admin user...")
        create_admin_user(db)
        print()
        
        # Seed cars
        print("Seeding car data...")
        cars_count = seed_cars(db)
        print()
        
        print("=" * 60)
        print("[OK] Seeding complete!")
        print(f"   - Admin user created")
        print(f"   - {cars_count} cars added to database")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

