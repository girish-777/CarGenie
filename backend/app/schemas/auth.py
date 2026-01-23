"""
Authentication schemas
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None

