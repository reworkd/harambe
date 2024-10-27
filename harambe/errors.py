from harambe.types import ScrapeResult, Schema


class HarambeException(Exception):
    """Base exception for all custom exceptions in Harambe."""

    pass


class SchemaValidationError(HarambeException):
    def __init__(self, _: Schema, __: ScrapeResult, message: str):
        # TODO: Remove the unused parameters everywhere
        super().__init__(message)


class CaptchaError(HarambeException):
    def __init__(self, message: str = "CAPTCHA was hit.") -> None:
        super().__init__(message)
