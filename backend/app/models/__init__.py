"""
Database models
"""
from app.models.user import User
from app.models.car import Car, CarSpec, CarScore
from app.models.favorite import Favorite
from app.models.review import Review
from app.models.alert import Alert
from app.models.price_history import PriceHistory

__all__ = [
    "User",
    "Car",
    "CarSpec",
    "CarScore",
    "Favorite",
    "Review",
    "Alert",
    "PriceHistory",
]

