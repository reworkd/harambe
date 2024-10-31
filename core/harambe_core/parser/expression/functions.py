from typing import Any
from slugify import slugify as python_slugify

from harambe_core.parser.expression.evaluator import ExpressionEvaluator


@ExpressionEvaluator.register("NOOP")
def noop(*args: Any) -> Any:
    return args[0] if len(args) == 1 else args


@ExpressionEvaluator.register("CONCAT")
def concat(*args: Any, seperator: str = "") -> str:
    return seperator.join(str(arg) for arg in args if arg is not None)


@ExpressionEvaluator.register("CONCAT_WS")
def concat_ws(seperator: str, *args: Any) -> str:
    return concat(*args, seperator=seperator)


@ExpressionEvaluator.register("COALESCE")
def coalesce(*args: Any) -> Any:
    for arg in args:
        if arg:
            return arg
    return None


@ExpressionEvaluator.register("SLUGIFY")
def slugify(*args: Any) -> str:
    text = concat_ws(" ", *args)
    return python_slugify(text)


@ExpressionEvaluator.register("UPPER")
def upper(text: str) -> str:
    return text.upper()


@ExpressionEvaluator.register("LOWER")
def lower(text: str) -> str:
    return text.lower()
