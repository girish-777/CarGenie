"""
Security utilities for password hashing and JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import logging
import sys
import warnings
from app.core.config import settings

logger = logging.getLogger(__name__)

# Suppress passlib/bcrypt warnings completely
warnings.filterwarnings('ignore')
# Suppress stderr output for bcrypt version check errors
class SuppressBcryptError:
    def __init__(self):
        self.stderr = sys.stderr
    def write(self, text):
        if 'bcrypt' in text.lower() or '__about__' in text.lower():
            return
        self.stderr.write(text)
    def flush(self):
        self.stderr.flush()

# Temporarily suppress stderr for passlib imports
_original_stderr = sys.stderr
sys.stderr = SuppressBcryptError()

try:
    # Try importing passlib to see if it causes errors, but we won't use it
    import passlib
except:
    pass
finally:
    sys.stderr = _original_stderr

# Use direct bcrypt only (no passlib)
USE_PASSLIB = False
pwd_context = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash using direct bcrypt"""
    try:
        # Handle both string and bytes
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
            
        if isinstance(plain_password, str):
            plain_bytes = plain_password.encode('utf-8')
        else:
            plain_bytes = plain_password
            
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"[Security] Bcrypt verify failed: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using direct bcrypt"""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"[Security] Bcrypt hash failed: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        if not token:
            logger.debug("[Security] Empty token provided")
            return None
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        # Don't log expired tokens as errors (they're expected)
        if "expired" in str(e).lower():
            logger.debug(f"[Security] Token expired: {e}")
        else:
            logger.debug(f"[Security] JWT decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"[Security] Unexpected error decoding token: {e}")
        return None

