from typing import Any


async def default_error_callback(url: str, status: int, *args):
    raise GotoError(url, status)


class HarambeException(Exception):
    """Base exception for all custom exceptions in Harambe."""

    pass


class UnknownHTMLConverter(HarambeException):
    def __init__(self, converter_type: Any) -> None:
        super().__init__(f"Unknown HTML converter type: {converter_type}")


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
