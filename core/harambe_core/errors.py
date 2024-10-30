class HarambeException(Exception):
    """Base exception for all custom exceptions in Harambe."""

    pass


class SchemaValidationError(HarambeException):
    def __init__(self, message: str = None):
        super().__init__(message)


class CaptchaError(HarambeException):
    def __init__(self, message: str = "CAPTCHA was hit.") -> None:
        super().__init__(message)
