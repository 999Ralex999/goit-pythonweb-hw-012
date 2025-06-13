from app.errors.base import AppError

class ContactExistsException(AppError):
    """
    Помилка при спробі створити контакт з вже існуючим email.
    """
    pass
