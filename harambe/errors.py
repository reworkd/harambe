from harambe.types import ScrapeResult, Schema


class HarambeException(Exception):
    """Base exception for all custom exceptions in this Harambe."""

    pass


class SchemaValidationError(HarambeException):
    def __init__(self, schema: Schema, data: ScrapeResult, message: str):
        super().__init__(
            "Data {data} does not match schema {schema}. {message}".format(
                data=data, schema=schema, message=message
            )
        )


class CaptchaError(HarambeException):
    def __init__(self, message="CAPTCHA was hit."):
        super().__init__(message)
