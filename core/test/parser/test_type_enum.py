import pytest
from pydantic import BaseModel, ValidationError

from harambe_core.parser.type_enum import ParserTypeEnum


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("male", "male"),
        ("Female", "FEMALE"),
        ("OTHER", "oThEr"),
        (" MAle ", "male")
    ]
)
def test_parser_success(input_value, expected_output):
    class Model(BaseModel):
        gender: ParserTypeEnum("male", 'FEMALE', "oThEr")

    model = Model(gender=input_value)
    assert model.gender == expected_output


@pytest.mark.parametrize(
    "input_, expected",
    [
        (dict(id="1", gender="male ", size="MEDIUM"), dict(id="1", gender="male", size="medium")),
        (dict(id="2", gender=" Female", size="LARGE "), dict(id="2", gender="female", size="large")),
        (dict(id="3", gender="OTHER", size="\t small\n"), dict(id="3", gender="other", size="small")),
    ]
)
def test_multiple_fields(input_, expected):
    class Model(BaseModel):
        id: str
        gender: ParserTypeEnum("male", 'female', "other")
        size: ParserTypeEnum("small", "medium", "large")

    model = Model(**input_)
    assert model.id == expected["id"]
    assert model.gender == expected["gender"]
    assert model.size == expected["size"]


@pytest.mark.parametrize(
    "invalid_value",
    [
        "invalid",
        "123"
        "",
        None,
        "MALEEE"
    ]
)
def test_invalid_parser_values(invalid_value):
    class Model(BaseModel):
        gender: ParserTypeEnum("male", "female", "other")

    with pytest.raises(ValidationError):
        Model(gender=invalid_value)


def test_optional_model():
    class Model(BaseModel):
        gender: ParserTypeEnum("male", "female", "other") | None

    model = Model(gender=None)
    assert model.gender is None

    model = Model(gender="male")
    assert model.gender == "male"


def test_default_model():
    class Model(BaseModel):
        gender: ParserTypeEnum("male", "female", "other") = "male"

    model = Model()
    assert model.gender == "male"

    model = Model(gender="female")
    assert model.gender == "female"
