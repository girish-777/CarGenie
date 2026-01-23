"""
Add descriptions for each car
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.database import SessionLocal
from app.models import Car

def add_descriptions():
    """Add descriptions to cars"""
    db = SessionLocal()
    
    try:
        cars = db.query(Car).all()
        print(f"Found {len(cars)} cars to update")
        
        descriptions = {
            'Toyota Camry': 'A reliable and fuel-efficient midsize sedan perfect for daily commuting. Known for its excellent resale value, comfortable ride, and advanced safety features. Great for families and professionals alike.',
            'BMW 3 Series': 'A luxury sports sedan that combines performance with elegance. Features responsive handling, premium interior, and cutting-edge technology. Ideal for drivers who want both comfort and driving excitement.',
            'BMW i4': 'An all-electric luxury sedan offering impressive range and performance. Zero emissions with BMW\'s signature driving dynamics. Perfect for eco-conscious drivers who don\'t want to compromise on luxury.',
            'Ford F-150 Lightning': 'The all-electric version of America\'s best-selling truck. Combines the power and capability of the F-150 with zero emissions. Features impressive towing capacity and advanced technology.',
            'Ford F-150': 'America\'s best-selling pickup truck for decades. Known for its durability, powerful engines, and impressive towing capacity. Perfect for work, recreation, and everyday use.',
            'Kia EV6': 'A stylish and efficient electric crossover with fast charging capability. Offers impressive range, modern design, and advanced tech features. Great choice for those entering the EV market.',
            'Kia Sportage': 'A versatile compact SUV with modern styling and practical features. Offers good fuel economy, comfortable interior, and excellent value. Perfect for families and urban driving.',
            'Mercedes-Benz C-Class': 'A premium compact luxury sedan with sophisticated design and advanced technology. Combines Mercedes-Benz quality with sporty performance. Ideal for those seeking luxury and refinement.',
            'Mercedes-Benz EQS': 'Mercedes-Benz\'s flagship all-electric luxury sedan. Features cutting-edge technology, exceptional range, and unparalleled comfort. The pinnacle of electric luxury vehicles.',
            'Toyota bZ4X': 'Toyota\'s first all-electric SUV offering reliability and efficiency. Features Toyota\'s legendary build quality with modern electric technology. Great for families making the switch to electric.'
        }
        
        for car in cars:
            key = f"{car.make} {car.model}"
            if key in descriptions:
                car.description = descriptions[key]
                print(f"Updated {car.year} {key}: Added description")
            else:
                # Generic description if not found
                car.description = f"A well-maintained {car.year} {car.make} {car.model}. This {car.condition} vehicle offers great value with {car.mileage:,} miles. Perfect for daily commuting and reliable transportation."
                print(f"Updated {car.year} {key}: Added generic description")
        
        db.commit()
        print(f"\nSuccessfully updated {len(cars)} car descriptions")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating descriptions: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_descriptions()

