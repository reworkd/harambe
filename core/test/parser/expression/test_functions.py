from harambe_core.parser.expression.functions import (
    lower,
    upper,
    slugify,
    coalesce,
    concat,
    noop,
)


def test_noop():
    assert noop(10) == 10
    assert noop(10, 20) == (10, 20)


def test_concat():
    assert concat("hello", "world") == "helloworld"
    assert concat("hello", None, "world") == "helloworld"
    assert concat(None, None) == ""


def test_coalesce():
    assert coalesce(None, None, "firstNonNull") == "firstNonNull"
    assert coalesce(None, False, 0, "", 1) == 1
    assert coalesce(None, None, None) is None


def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify(" Hello   World!  ") == "hello-world"
    assert slugify("Hello-World") == "hello-world"


def test_upper():
    assert upper("hello") == "HELLO"
    assert upper("Hello World") == "HELLO WORLD"


def test_lower():
    assert lower("HELLO") == "hello"
    assert lower("Hello World") == "hello world"
