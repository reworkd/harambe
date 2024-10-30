import re
from typing import Any

from harambe_core.parser.expression.evaluator import ExpressionEvaluator


@ExpressionEvaluator.register("NOOP")
def noop(*args: Any) -> Any:
    return args[0] if len(args) == 1 else args


@ExpressionEvaluator.register("CONCAT")
def concat(*args: str) -> str:
    return "".join(str(arg) for arg in args if arg is not None)


@ExpressionEvaluator.register("COALESCE")
def coalesce(*args: Any) -> Any:
    for arg in args:
        if arg:
            return arg
    return None


@ExpressionEvaluator.register("SLUGIFY")
def slugify(*args: str) -> str:
    text = concat(*args)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


@ExpressionEvaluator.register("UPPER")
def upper(text: str) -> str:
    return text.upper()


@ExpressionEvaluator.register("LOWER")
def lower(text: str) -> str:
    return text.lower()
