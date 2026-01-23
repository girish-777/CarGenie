"""
Setup script to initialize the database
"""
import sys
import os

# Add backend to path (go up one level from db_deploy to project root, then into backend)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.db.database import engine, Base
from app.models import *  # Import all models

def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()

