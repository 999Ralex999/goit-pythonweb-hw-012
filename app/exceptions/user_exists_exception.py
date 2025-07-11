class UserExistsException(Exception):
    """
    Exception for when a user already exists
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
