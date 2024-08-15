from harambe import SDK
from harambe.ast_overrides import float_override, override_builtins
import pytest


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (" 123.45 ", 123.45),
        ("$123.45", 123.45),
        ("1,234.56", 1234.56),
        ("$1,234.56", 1234.56),
        (1234, 1234.0),
        (1234.56, 1234.56),
        ("  $1,234.56  ", 1234.56),
        ("123", 123.0),
    ],
)
def test_float_override(input_value, expected_output):
    assert float_override(input_value) == expected_output


@pytest.mark.parametrize(
    "input_value, exception", [("invalid", ValueError), (None, TypeError)]
)
def test_float_override_exceptions(input_value, exception):
    with pytest.raises(exception):
        float_override(input_value)


def test_override_builtins():
    def function():
        return float("$1")

    with pytest.raises(ValueError):
        function()

    new_func = override_builtins(function, {"SDK": SDK, "observer": None})
    assert new_func() == 1.000


def test_override_builtins_var():
    def function():
        return float

    with pytest.raises(ValueError):
        function()("1$")

    new_func = override_builtins(function, {"SDK": SDK, "observer": None})
    assert new_func()("$1") == 1.0
