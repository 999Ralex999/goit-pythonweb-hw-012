class TokenDecodeException(Exception):
    """
    Exception for when a token cannot be decoded
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
