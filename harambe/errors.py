from harambe.types import ScrapeResult, Schema


class HarambeException(Exception):
    """Base exception for all custom exceptions in Harambe."""

    pass


class SchemaValidationError(HarambeException):
    def __init__(self, schema: Schema, data: ScrapeResult, message: str):
        super().__init__(f"Data {data} does not match schema {schema}. {message}")


class MissingRequiredFieldsError(SchemaValidationError):
    def __init__(self, schema: Schema, data: ScrapeResult, missing_fields: list[str]):
        message = f"Missing required fields: {', '.join(missing_fields)}"
        super().__init__(schema, data, message)
        self.missing_fields = missing_fields


class CaptchaError(HarambeException):
    def __init__(self, message="CAPTCHA was hit."):
        super().__init__(message)
