import json
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path


@lru_cache
def load_schema(name: str, make_all_required: bool = False, exclude: str = "") -> dict:
    path = Path(__file__).parent / f"{name}.json"
    with open(path) as f:
        schema = json.loads(f.read())

    if make_all_required:
        schema = _make_all_required(schema, set(exclude.split(",")))

    return schema


def _make_all_required(schema: dict, exclude: set[str]) -> dict:
    for key, value in schema.items():
        if isinstance(value, dict):
            if "type" in value and isinstance(value["type"], str):
                value["required"] = key not in exclude

            _make_all_required(value, exclude)
        elif isinstance(value, list):
            for item in value:
                _make_all_required(item, exclude)
    return schema
