"""
Bootstrap file for importing all database models.
Import this file to ensure all models are registered with SQLAlchemy metadata.
"""

from app.entity.base import Base
from app.entity.contact import Contact
from app.entity.user import User


__all__ = ["Base"]
