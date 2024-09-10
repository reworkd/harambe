from harambe.types import ScrapeResult, Schema


class SchemaValidationError(Exception):
    def __init__(self, schema: Schema, data: ScrapeResult, message: str):
        super().__init__(
            "Data {data} does not match schema {schema}. {message}".format(
                data=data, schema=schema, message=message
            )
        )


class CaptchaError(Exception):
    def __init__(self, message="CAPTCHA was hit."):
        self.message = message
        super().__init__(self.message)
