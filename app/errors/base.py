class AppError(Exception):
    """
    Базовий клас для всіх користувацьких помилок застосунку.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
