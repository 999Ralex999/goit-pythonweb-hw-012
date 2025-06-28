class TokenExpiredException(Exception):
    """
    Exception for when a token has expired
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
