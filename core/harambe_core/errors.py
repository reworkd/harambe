class HarambeException(Exception):
    """Base exception for all custom exceptions in Harambe."""

    pass


class GotoError(HarambeException):
    def __init__(self, url: str, status: int) -> None:
        super().__init__(
            f'Error calling goto("{url}"). Received unexpected status code: {status}'
        )


class SchemaValidationError(HarambeException):
    def __init__(self, message: str = None):
        super().__init__(message)


class CaptchaError(HarambeException):
    def __init__(self, message: str = "CAPTCHA was hit.") -> None:
        super().__init__(message)
