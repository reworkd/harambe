from harambe.types import ScrapeResult, Schema


class HarambeException(Exception):
    """Base exception for all custom exceptions in Harambe."""

    pass


class SchemaValidationError(HarambeException):
    def __init__(self, schema: Schema, data: ScrapeResult, message: str):
        super().__init__(f"Data {data} does not match schema {schema}. {message}")


class CaptchaError(HarambeException):
    def __init__(self, message="CAPTCHA was hit."):
        super().__init__(message)
