from typing import Any, Generator

from slugify import slugify as python_slugify

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


@ExpressionEvaluator.define_builtin("SUBSTRING_AFTER")
def substring_after(input_string: str, delimiter: str) -> str:
    """
    Returns the substring after the first occurrence of the specified delimiter.

    Args:
        input_string: The string to extract from
        delimiter: The substring to search for

    Returns:
        The substring after the first occurrence of the delimiter.
        If the delimiter is not found, returns the original string.
    """
    if delimiter == "":
        raise ValueError("SUBSTRING_AFTER requires a non-empty delimiter to search for")

    parts = input_string.split(delimiter, 1)
    if len(parts) == 1:
        return input_string

    return parts[1]


def flatten(values: Any) -> Generator[Any, None, None]:
    for value in values:
        if isinstance(value, list):
            yield from flatten(value)
        else:
            yield value
