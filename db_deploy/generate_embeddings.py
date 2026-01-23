"""
Script to generate embeddings for all cars in the database
Run this after setting up ChromaDB and OpenAI API key
"""
import sys
import os

# Add backend to path (go up one level from db_deploy to project root, then into backend)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models import Car
from app.core.embeddings import EmbeddingsService
from app.core.vectordb import VectorDB
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_all_embeddings():
    """Generate and store embeddings for all cars"""
    db: Session = SessionLocal()
    
    try:
        # Initialize services
        embeddings_service = EmbeddingsService()
        vectordb = VectorDB()
        
        if not embeddings_service.client:
            logger.error("❌ OpenAI API key not set. Please set OPENAI_API_KEY in .env file")
            return
        
        # Get all cars
        cars = db.query(Car).filter(Car.is_available == True).all()
        total_cars = len(cars)
        
        logger.info(f"============================================================")
        logger.info(f"Generating Embeddings for {total_cars} Cars")
        logger.info(f"============================================================")
        
        success_count = 0
        fail_count = 0
        
        for i, car in enumerate(cars, 1):
            logger.info(f"[{i}/{total_cars}] Processing: {car.year} {car.make} {car.model} (ID: {car.id})")
            
            try:
                # Generate embedding
                embedding = embeddings_service.generate_car_embedding(
                    make=car.make,
                    model=car.model,
                    year=car.year,
                    description=car.description,
                    fuel_type=car.fuel_type,
                    transmission=car.transmission
                )
                
                if not embedding:
                    logger.warning(f"  ⚠️  Failed to generate embedding")
                    fail_count += 1
                    continue
                
                # Prepare metadata
                metadata = {
                    "make": car.make,
                    "model": car.model,
                    "year": car.year,
                    "price": car.price,
                    "fuel_type": car.fuel_type,
                    "transmission": car.transmission,
                    "description": car.description or ""
                }
                
                # Store in vector DB
                success = vectordb.add_car_embedding(
                    car_id=car.id,
                    embedding=embedding,
                    metadata=metadata
                )
                
                if success:
                    logger.info(f"  ✅ Embedding generated and stored")
                    success_count += 1
                else:
                    logger.warning(f"  ⚠️  Failed to store embedding")
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"  ❌ Error: {e}")
                fail_count += 1
        
        logger.info(f"============================================================")
        logger.info(f"✅ Embedding Generation Complete!")
        logger.info(f"   - Success: {success_count}")
        logger.info(f"   - Failed: {fail_count}")
        logger.info(f"   - Total embeddings in DB: {vectordb.get_collection_count()}")
        logger.info(f"============================================================")
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    generate_all_embeddings()
