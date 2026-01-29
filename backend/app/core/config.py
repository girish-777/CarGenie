"""
Application configuration settings

Simple class-based approach that manually loads environment variables.
This avoids Pydantic Settings' automatic environment variable parsing which causes issues
with variables like `window.BACKEND_URL`.
"""

import os
from typing import Optional, Union

from dotenv import dotenv_values

# Calculate project root: backend/app/core/config.py -> go up 3 levels
_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_project_root = os.path.dirname(_base_dir)  # Go up one more level from backend/
_db_path = os.path.join(_project_root, "automobile.db").replace("\\", "/")
_env_file_path = os.path.join(_project_root, ".env")


def _get_env(key: str, default: str = None) -> Optional[str]:
    """Get environment variable, checking both .env file and os.environ, filtering invalid keys"""
    # Skip variables with dots (like window.BACKEND_URL) or starting with 'window'
    if '.' in key or key.startswith('window'):
        return default
    
    # Check os.environ first (but skip problematic vars)
    value = os.environ.get(key)
    if value and '.' not in key and not key.startswith('window'):
        return value
    
    # Check .env file
    if os.path.exists(_env_file_path):
        try:
            env_vars = dotenv_values(_env_file_path) or {}
            value = env_vars.get(key)
            if value and '.' not in key and not key.startswith('window'):
                return value
        except Exception:
            pass
    
    return default


class Settings:
    """Application settings - simple class-based approach to avoid Pydantic env var issues"""
    
    def __init__(self):
        # Database - Use absolute path to project root
        self.DATABASE_URL: str = _get_env('DATABASE_URL', f"sqlite:///{_db_path}")
        
        # Security
        self.SECRET_KEY: str = _get_env('SECRET_KEY', "your-secret-key-change-in-production")
        self.ALGORITHM: str = _get_env('ALGORITHM', "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(_get_env('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
        
        # CORS - Allow localhost origins for development
        # Note: Can't use ["*"] with allow_credentials=True, so list specific origins
        cors_origins_str = _get_env('CORS_ORIGINS', '*')
        if cors_origins_str == '*':
            # Default to common localhost ports for development
            self.CORS_ORIGINS: list[str] = [
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "http://localhost:8080",
                "http://127.0.0.1:8080",
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        else:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
        
        # OpenAI (for future use)
        self.OPENAI_API_KEY: Optional[str] = _get_env('OPENAI_API_KEY')


# Initialize settings
settings = Settings()

