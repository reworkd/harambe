import pytest
from pydantic import ValidationError, BaseModel

from harambe_core.parser.type_email import ParserTypeEmail


class _TestModel(BaseModel):
    email: ParserTypeEmail


@pytest.mark.parametrize(
    "email, expected",
    [
        (
            "mailto:segreteria.capogabinetto@ministeroturismo.gov.it",
            "segreteria.capogabinetto@ministeroturismo.gov.it",
        ),
        ("John Doe <john.doe@example.com>", "john.doe@example.com"),
        ("jane@doe.com", "jane@doe.com"),
        ("email@sub.sub.domain.com", "email@sub.sub.domain.com"),
        ("user@example.museum", "user@example.museum"),
        ("Jane.Doe@Example.COM", "jane.doe@example.com"),
        ("special+chars@123.com", "special+chars@123.com"),
        ("jane@doe.com.", "jane@doe.com"),
        ("user@example.museum..", "user@example.museum"),
        ("Jane.Doe@Example.COM...", "jane.doe@example.com"),
        ("mailto:test@example.com....", "test@example.com"),
        ("test@example.com...  ", "test@example.com"),
    ],
)
def test_parser_success(email, expected):
    model = _TestModel(email=email)
    assert model.email == expected


@pytest.mark.parametrize(
    "invalid_email",
    ["invalid", "invalid@", "invalid@.", "invalid@.com", "invalid@com.", 123, None],
)
def test_parser_fail(invalid_email):
    with pytest.raises(ValidationError):
        _TestModel(email=invalid_email)
