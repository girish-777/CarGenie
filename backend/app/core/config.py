"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator
import os
import urllib.request
import logging

logger = logging.getLogger(__name__)

# Calculate project root: backend/app/core/config.py -> go up 3 levels
_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_project_root = os.path.dirname(_base_dir)  # Go up one more level from backend/
_db_deploy_dir = os.path.join(_project_root, 'db_deploy').replace('\\', '/')
_db_path = os.path.join(_db_deploy_dir, 'automobile.db').replace('\\', '/')
_env_file_path = os.path.join(_project_root, ".env")

# Render database service URL - can be set via environment variable
RENDER_DB_URL = os.environ.get('RENDER_DB_URL', 'https://cargenie-db-latest.onrender.com')
# Flag to enable downloading database from Render service
SYNC_DB_FROM_RENDER = os.environ.get('SYNC_DB_FROM_RENDER', 'true').lower() == 'true'

def download_database_from_render(force=False):
    """Download database file from Render database service"""
    if not SYNC_DB_FROM_RENDER and not force:
        logger.info("Database sync from Render is disabled")
        return False
        
    try:
        # Ensure db_deploy directory exists
        os.makedirs(_db_deploy_dir, exist_ok=True)
        
        # Download database file from Render
        db_url = f"{RENDER_DB_URL}/automobile.db"
        logger.info(f"Downloading database from {db_url}")
        
        urllib.request.urlretrieve(db_url, _db_path)
        logger.info(f"Database downloaded successfully to {_db_path}")
        return True
    except Exception as e:
        logger.warning(f"Failed to download database from Render: {e}")
        if not os.path.exists(_db_path):
            logger.error(f"No local database found at {_db_path} and download failed!")
        else:
            logger.info(f"Using existing local database at {_db_path}")
        return False


# Try to download database on module load if enabled
if SYNC_DB_FROM_RENDER and not os.environ.get('DATABASE_URL'):
    # Always try to sync from Render (will use local if download fails)
    download_database_from_render()
elif os.path.exists(_db_path):
    logger.info(f"Using existing local database at {_db_path}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database - Use absolute path to project root
    # Can be overridden with DATABASE_URL environment variable
    DATABASE_URL: str = os.environ.get('DATABASE_URL', f"sqlite:///{_db_path}")
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - can be a string (comma-separated) or list
    # Default includes localhost and common Render frontend URLs
    CORS_ORIGINS: Union[str, list[str]] = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,https://cargenie-frontend.onrender.com"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list"""
        if isinstance(v, str):
            # If it's "*", return ["*"] (but note: cannot use with allow_credentials=True)
            if v.strip() == "*":
                return ["*"]
            # Otherwise split by comma
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else ["*"]
        return v
    
    # OpenAI (for future use)
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        # Look for .env file in project root (one level up from backend/)
        env_file = _env_file_path
        case_sensitive = True
        extra = 'ignore'  # Ignore extra environment variables not defined in the model


settings = Settings()

