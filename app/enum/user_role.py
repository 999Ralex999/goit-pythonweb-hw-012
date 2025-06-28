from enum import Enum


class UserRole(str, Enum):
    """
    User role enum
    """

    USER = "USER"
    ADMIN = "ADMIN"
