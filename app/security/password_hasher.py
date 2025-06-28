from passlib.context import CryptContext


class PasswordHasher:
    """
    Password hasher

    Attributes:
        pwd_context (CryptContext): The password hasher
    """

    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        Hash password

        Args:
            password (str): The password to hash

        Returns:
            str: The hashed password
        """
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password

        Args:
            password (str): The password to verify
            hashed_password (str): The hashed password to verify

        Returns:
            bool: True if the password is valid, False otherwise
        """
        return self.pwd_context.verify(password, hashed_password)


password_hasher = PasswordHasher()
