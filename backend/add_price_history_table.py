"""
Migration script to add price_history table
"""
import sys
import os
import sqlite3

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings

def add_price_history_table():
    """Add price_history table if it doesn't exist"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        print("Run setup.py first to create the database.")
        return
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='price_history'
        """)
        
        if cursor.fetchone():
            print("Table 'price_history' already exists. Skipping migration.")
        else:
            print("Creating 'price_history' table...")
            cursor.execute("""
                CREATE TABLE price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    car_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (car_id) REFERENCES cars (id),
                    CONSTRAINT idx_car_recorded UNIQUE (car_id, recorded_at)
                )
            """)
            
            # Create index
            cursor.execute("""
                CREATE INDEX idx_car_recorded ON price_history (car_id, recorded_at)
            """)
            
            conn.commit()
            print("Table 'price_history' created successfully!")
            
            # Populate initial price history for existing cars
            print("Populating initial price history for existing cars...")
            cursor.execute("""
                INSERT INTO price_history (car_id, price, recorded_at)
                SELECT id, price, created_at FROM cars
            """)
            conn.commit()
            print("Initial price history populated!")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_price_history_table()

