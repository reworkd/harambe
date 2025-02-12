from harambe_core.parser.expression.functions import (
    lower,
    upper,
    slugify,
    coalesce,
    concat,
    noop,
    concat_ws,
)


def test_noop():
    assert noop(10) == 10
    assert noop(10, 20) == (10, 20)


def test_concat():
    assert concat("hello", "world") == "helloworld"
    assert concat("hello", None, "world") == "helloworld"
    assert concat(None, None) == ""
    assert concat(["hello", "world"]) == "helloworld"
    assert concat(["hello"], "world") == "helloworld"
    assert concat(["hello"], ["world"]) == "helloworld"


def test_concat_ws():
    assert concat_ws(" ", "hello", "world") == "hello world"
    assert concat_ws(",", "hello", "world") == "hello,world"
    assert concat_ws(":-:", "hello", None, "world") == "hello:-:world"
    assert concat_ws(" ", ["hello", "world"]) == "hello world"
    assert concat_ws(" ", ["hello"], "world") == "hello world"
    assert concat_ws(" ", [], "hello", "world") == "hello world"
    assert concat_ws("-", ["hello"], ["world", "!"], [""]) == "hello-world-!"


def test_coalesce():
    assert coalesce(None, None, "firstNonNull") == "firstNonNull"
    assert coalesce(None, False, 0, "", 1) == 1
    assert coalesce(None, None, None) is None


def test_slugify():
    assert slugify("Hello World!") == "hello-world"
    assert slugify(" Hello   World!  ") == "hello-world"
    assert slugify("Hello-World") == "hello-world"
    assert slugify("Hello World", "Another") == "hello-world-another"
    assert slugify("Hello World", "Another", 2) == "hello-world-another-2"
    assert slugify(1, 2, 3, "four") == "1-2-3-four"


def test_upper():
    assert upper("hello") == "HELLO"
    assert upper("Hello World") == "HELLO WORLD"


def test_lower():
    assert lower("HELLO") == "hello"
    assert lower("Hello World") == "hello world"
