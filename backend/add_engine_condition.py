"""
Migration script to add engine_condition column to existing cars table
"""
import sys
import os
import sqlite3

# Add backend to path
backend_dir = os.path.dirname(__file__)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings

def add_engine_condition_column():
    """Add engine_condition column to cars table if it doesn't exist"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        print("Run setup.py first to create the database.")
        return
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(cars)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "engine_condition" in columns:
            print("Column 'engine_condition' already exists. Skipping migration.")
        else:
            print("Adding 'engine_condition' column to cars table...")
            cursor.execute("ALTER TABLE cars ADD COLUMN engine_condition VARCHAR")
            conn.commit()
            print("Column 'engine_condition' added successfully!")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_engine_condition_column()

