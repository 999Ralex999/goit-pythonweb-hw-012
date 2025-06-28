class ContactExistsException(Exception):
    """
    Exception for when a contact already exists
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
