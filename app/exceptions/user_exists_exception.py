class UserExistsException(Exception):
    def __init__(self, message="Користувач вже існує"):
        self.message = message
        super().__init__(self.message)

