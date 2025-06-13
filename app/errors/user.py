from app.errors.base import AppError

class UserExistsException(AppError):
    """
    Помилка при спробі зареєструвати користувача з вже існуючим username або email.
    """
    pass
