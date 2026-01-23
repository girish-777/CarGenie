"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator
import os


# Calculate project root: backend/app/core/config.py -> go up 3 levels
_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_project_root = os.path.dirname(_base_dir)  # Go up one more level from backend/
_db_path = os.path.join(_project_root, 'automobile.db').replace('\\', '/')
_env_file_path = os.path.join(_project_root, ".env")

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database - Use absolute path to project root
    DATABASE_URL: str = f"sqlite:///{_db_path}"
    
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

