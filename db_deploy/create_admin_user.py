"""
Simple script to create admin user with default credentials
"""
import sys
import os

# Add backend to path (go up one level from db_deploy to project root, then into backend)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))

from app.db.database import SessionLocal, engine
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import text

def create_admin():
    """Create admin user with default credentials"""
    db = SessionLocal()
    try:
        # First, add is_admin column if it doesn't exist
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0"))
                conn.commit()
                print("Added is_admin column to users table")
        except Exception as e:
            # Column might already exist, that's okay
            if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                print(f"Note: {e}")
        
        email = "admin@cargenie.com"
        password = "admin123"
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Update existing user to admin
            existing_user.is_admin = True
            existing_user.hashed_password = get_password_hash(password)
            existing_user.is_active = True
            db.commit()
            print(f"SUCCESS: Admin user '{email}' updated successfully!")
        else:
            # Create new admin user
            hashed_password = get_password_hash(password)
            admin_user = User(
                email=email,
                hashed_password=hashed_password,
                full_name="Admin User",
                is_admin=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"SUCCESS: Admin user '{email}' created successfully!")
        
        print("\n" + "="*50)
        print("Admin Credentials:")
        print("="*50)
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("="*50)
        print("\nYou can now login with these credentials!")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

