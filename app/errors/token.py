from app.errors.base import AppError

class TokenDecodeException(AppError):
    """
    Помилка при декодуванні JWT-токена.
    """
    pass

class TokenExpiredException(AppError):
    """
    Помилка при використанні простроченого JWT-токена.
    """
    pass
