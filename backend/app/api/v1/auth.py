"""
Authentication API endpoints
"""
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import Token, TokenData
from app.schemas.user import UserCreate, UserResponse, UserUpdate, PasswordChange
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    logger.debug(f"[DEBUG] get_current_user: Validating token")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        logger.debug(f"[DEBUG] get_current_user: No token provided")
        raise credentials_exception
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            logger.debug(f"[DEBUG] get_current_user: Token decode failed - invalid or expired token")
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            logger.warning(f"[DEBUG] get_current_user: No email in token payload")
            raise credentials_exception
        
        logger.debug(f"[DEBUG] get_current_user: Token valid, email: {email}")
        token_data = TokenData(email=email)
        user = db.query(User).filter(User.email == token_data.email).first()
        
        if user is None:
            logger.warning(f"[DEBUG] get_current_user: User not found for email {email}")
            raise credentials_exception
        
        logger.debug(f"[DEBUG] get_current_user: User authenticated (ID: {user.id})")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[DEBUG] get_current_user: Unexpected error: {e}")
        raise credentials_exception


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, return None if not (doesn't raise exception)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    if not token:
        return None
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None
        
        email: str = payload.get("sub")
        if email is None:
            return None
        
        token_data = TokenData(email=email)
        user = db.query(User).filter(User.email == token_data.email).first()
        
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user if they are an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account"""
    logger.info(f"[DEBUG] signup: Signup request for email {user_data.email}")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"[DEBUG] signup: Email {user_data.email} already registered")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    logger.debug(f"[DEBUG] signup: Creating new user with email {user_data.email}")
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"[DEBUG] signup: User created successfully (ID: {db_user.id})")
    
    return db_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    logger.info(f"[DEBUG] login: Login attempt for email {form_data.username}")
    
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user:
        logger.warning(f"[DEBUG] login: User {form_data.username} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"[DEBUG] login: User found (ID: {user.id}), verifying password")
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"[DEBUG] login: Password verification failed for user {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        logger.warning(f"[DEBUG] login: User {form_data.username} is inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    logger.debug(f"[DEBUG] login: Creating access token for user {user.id}")
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    logger.info(f"[DEBUG] login: Login successful for user {user.id}, token created")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile (name)"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password length
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

