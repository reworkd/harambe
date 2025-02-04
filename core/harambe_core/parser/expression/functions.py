from slugify import slugify as python_slugify
from typing import Any, Generator

from harambe_core.parser.expression.evaluator import ExpressionEvaluator


@ExpressionEvaluator.define_builtin("NOOP")
def noop(*args: Any) -> Any:
    return args[0] if len(args) == 1 else args


@ExpressionEvaluator.define_builtin("CONCAT")
def concat(*args: Any, seperator: str = "") -> str:
    args = [a for a in flatten(args) if a is not None and a != ""]
    return seperator.join(str(arg) for arg in args)


@ExpressionEvaluator.define_builtin("CONCAT_WS")
def concat_ws(seperator: str, *args: Any) -> str:
    return concat(*args, seperator=seperator)


@ExpressionEvaluator.define_builtin("COALESCE")
def coalesce(*args: Any) -> Any:
    for arg in args:
        if arg:
            return arg
    return None


@ExpressionEvaluator.define_builtin("SLUGIFY")
def slugify(*args: Any) -> str:
    text = concat_ws("-", *args)
    return python_slugify(text)


@ExpressionEvaluator.define_builtin("UPPER")
def upper(text: str) -> str:
    return text.upper()


@ExpressionEvaluator.define_builtin("LOWER")
def lower(text: str) -> str:
    return text.lower()


def flatten(values: Any) -> Generator[Any, None, None]:
    for value in values:
        if isinstance(value, list):
            yield from flatten(value)
        else:
            yield value
