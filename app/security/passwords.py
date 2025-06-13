from passlib.context import CryptContext

class PasswordHasher:
    """
    Клас для хешування та перевірки паролів.
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        Хешування паролю.
        """
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Перевірка паролю.
        """
        return self.pwd_context.verify(password, hashed_password)


password_hasher = PasswordHasher()

