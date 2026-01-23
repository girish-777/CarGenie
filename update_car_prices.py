"""
Update car prices to realistic values
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.database import SessionLocal
from app.models import Car

def update_car_prices():
    """Update car prices for used cars based on engine condition"""
    db = SessionLocal()
    try:
        # Base prices for NEW cars (MSRP)
        new_car_prices = {
            # Toyota
            ('Toyota', 'Camry', 2023): 28000,
            ('Toyota', 'bZ4X', 2024): 42000,
            
            # BMW
            ('BMW', 'i4', 2024): 56000,
            ('BMW', '3 Series', 2023): 45000,
            
            # Ford
            ('Ford', 'F-150 Lightning', 2024): 60000,
            ('Ford', 'F-150', 2024): 40000,
            
            # Kia
            ('Kia', 'EV6', 2024): 48000,
            ('Kia', 'Sportage', 2024): 28000,
            
            # Mercedes-Benz
            ('Mercedes-Benz', 'C-Class', 2024): 47000,
            ('Mercedes-Benz', 'EQS', 2024): 110000,
        }
        
        # Engine condition multipliers (for used cars)
        # These represent what % of new price based on engine condition
        condition_multipliers = {
            'excellent': 0.88,  # 88% of new price
            'good': 0.78,       # 78% of new price
            'fair': 0.65,       # 65% of new price
        }
        
        # Age depreciation (per year)
        current_year = 2024
        age_depreciation_per_year = 0.05  # 5% per year
        
        updated_count = 0
        
        for car in db.query(Car).all():
            key = (car.make, car.model, car.year)
            if key in new_car_prices:
                new_price = new_car_prices[key]
                
                # Calculate age depreciation
                car_age = current_year - car.year
                age_multiplier = 1 - (age_depreciation_per_year * car_age)
                
                # Get engine condition multiplier
                engine_condition = (car.engine_condition or 'good').lower()
                condition_mult = condition_multipliers.get(engine_condition, 0.75)
                
                # Calculate used car price
                used_price = new_price * age_multiplier * condition_mult
                
                # Round to nearest 500
                used_price = round(used_price / 500) * 500
                
                if car.price != used_price:
                    old_price = car.price
                    car.price = used_price
                    updated_count += 1
                    print(f"[OK] {car.year} {car.make} {car.model} (Engine: {engine_condition}): ${old_price:,.0f} -> ${used_price:,.0f}")
        
        db.commit()
        print(f"\n[SUCCESS] Updated {updated_count} car prices based on engine condition")
        
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
    print("Updating Car Prices")
    print("=" * 60)
    print()
    update_car_prices()
    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)

