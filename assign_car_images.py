"""
Simple script to assign local images to cars
Only uses images from frontend/images/ folder
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.database import SessionLocal
from app.models import Car

def assign_car_images():
    """Assign local images to cars based on make/model/year"""
    db = SessionLocal()
    try:
        # Available local images (updated with new .jpeg files)
        available_images = [
            'images/2023-Toyota-Camry.webp',
            'images/2024 BMW i4.jpeg',
            'images/2024 Ford F-150 Lightning.jpeg',
            'images/2024 Ford F-150.jpg',
            'images/2024 Kia EV6.jpeg',
            'images/2024 Kia Sportage.jpeg',
            'images/2024 Mercedes-Benz C-Class.jpeg',
            'images/2024 Mercedes-Benz EQS.jpg',
            'images/2024 Toyota bZ4X.jpeg',
            'images/BMW 3 Series.jpeg',
        ]
        
        # Simple mapping: make/model -> image (using updated .jpeg files)
        image_mapping = {
            # Toyota
            ('Toyota', 'Camry'): 'images/2023-Toyota-Camry.webp',
            ('Toyota', 'bZ4X'): 'images/2024 Toyota bZ4X.jpeg',
            ('Toyota', None): 'images/2023-Toyota-Camry.webp',  # Default Toyota
            
            # BMW
            ('BMW', 'i4'): 'images/2024 BMW i4.jpeg',
            ('BMW', '3 Series'): 'images/BMW 3 Series.jpeg',
            ('BMW', None): 'images/BMW 3 Series.jpeg',  # Default BMW
            
            # Ford
            ('Ford', 'F-150 Lightning'): 'images/2024 Ford F-150 Lightning.jpeg',
            ('Ford', 'F-150'): 'images/2024 Ford F-150.jpg',
            ('Ford', None): 'images/2024 Ford F-150.jpg',  # Default Ford
            
            # Kia
            ('Kia', 'EV6'): 'images/2024 Kia EV6.jpeg',
            ('Kia', 'Sportage'): 'images/2024 Kia Sportage.jpeg',
            ('Kia', None): 'images/2024 Kia EV6.jpeg',  # Default Kia
            
            # Mercedes-Benz
            ('Mercedes-Benz', 'C-Class'): 'images/2024 Mercedes-Benz C-Class.jpeg',
            ('Mercedes-Benz', 'EQS'): 'images/2024 Mercedes-Benz EQS.jpg',
            ('Mercedes-Benz', None): 'images/2024 Mercedes-Benz C-Class.jpeg',  # Default Mercedes
        }
        
        # Get all cars from database
        cars = db.query(Car).all()
        updated_count = 0
        
        for car in cars:
            # Always check and assign correct image
            needs_update = False
            if not car.image_urls or len(car.image_urls) == 0:
                needs_update = True
            elif car.image_urls and len(car.image_urls) > 0:
                img_url = car.image_urls[0] if isinstance(car.image_urls, list) else str(car.image_urls)
                # Update if it's an Unsplash URL
                if 'unsplash.com' in img_url or 'unsplash' in img_url.lower():
                    needs_update = True
                else:
                    # Check if the car has the correct image based on mapping
                    key = (car.make, car.model)
                    expected_image = None
                    if key in image_mapping and image_mapping[key] is not None:
                        expected_image = image_mapping[key]
                    elif (car.make, None) in image_mapping and image_mapping[(car.make, None)] is not None:
                        expected_image = image_mapping[(car.make, None)]
                    
                    if expected_image and img_url != expected_image:
                        needs_update = True
            
            if not needs_update:
                continue
            
            # Try exact match (make, model)
            key = (car.make, car.model)
            if key in image_mapping and image_mapping[key] is not None:
                car.image_urls = [image_mapping[key]]
                updated_count += 1
                print(f"[OK] Assigned {image_mapping[key]} to {car.year} {car.make} {car.model} (ID: {car.id})")
                continue
            
            # Try match by make only
            key = (car.make, None)
            if key in image_mapping and image_mapping[key] is not None:
                car.image_urls = [image_mapping[key]]
                updated_count += 1
                print(f"[OK] Assigned {image_mapping[key]} to {car.year} {car.make} {car.model} (ID: {car.id})")
                continue
            
            # For cars without specific images (Honda, Hyundai, etc.), assign from available images
            # Use car ID to select image (ensures different cars get different images)
            image_index = car.id % len(available_images)
            selected_image = available_images[image_index]
            car.image_urls = [selected_image]
            updated_count += 1
            print(f"[OK] Assigned {selected_image} to {car.year} {car.make} {car.model} (ID: {car.id})")
        
        db.commit()
        print(f"\n[SUCCESS] Updated {updated_count} cars with local images")
        
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
    print("Assigning Local Images to Cars")
    print("=" * 60)
    print()
    assign_car_images()
    print()
    print("=" * 60)
    print("Done!")
    print("=" * 60)
