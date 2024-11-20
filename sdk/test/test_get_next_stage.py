import pytest

from harambe.core import get_next_stage
from harambe.types import Stage


@pytest.mark.parametrize(
    "previous_stage,expected_stage",
    [
        ("parent_category", "category"),
        ("category", "listing"),
        ("listing", "detail"),
        ("detail", "detail"),
        (None, "detail"),
    ],
)
def test_get_next_stage(previous_stage: Stage, expected_stage: Stage):
    result = get_next_stage(previous_stage)
    assert result == expected_stage
