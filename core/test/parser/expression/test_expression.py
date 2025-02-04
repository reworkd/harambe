import pytest

from harambe_core.parser.expression import ExpressionEvaluator


@pytest.fixture
def evaluator():
    return ExpressionEvaluator()


def test_evaluate_literal(evaluator):
    assert evaluator.evaluate("'hello'", {}) == "hello"
    assert evaluator.evaluate('"hello"', {}) == "hello"


def test_evaluate_single_variable(evaluator):
    assert evaluator.evaluate("name", {"name": "adam"}) == "adam"


def test_evaluate_single_func(evaluator):
    assert evaluator.evaluate("UPPER('hello')", {}) == "HELLO"
    assert evaluator.evaluate("CONCAT('hello', 'world')", {}) == "helloworld"
    assert evaluator.evaluate("COALESCE('', 'world')", {}) == "world"


def test_evaluate_case_insensitive(evaluator):
    assert evaluator.evaluate("upper('hello')", {}) == "HELLO"


def test_evaluate_string_literal_quotes(evaluator):
    assert evaluator.evaluate('upper("hello")', {}) == "HELLO"


def test_evaluate_from_context(evaluator):
    assert evaluator.evaluate("UPPER(name)", {"name": "hello"}) == "HELLO"
    assert (
        evaluator.evaluate("CONCAT(name, 'world')", {"name": "hello"}) == "helloworld"
    )
    assert (
        evaluator.evaluate("COALESCE(world, name)", {"name": "adam", "good": False})
        == "adam"
    )


def test_evaluate_from_context_object_of_objects(evaluator):
    assert (
        evaluator.evaluate("UPPER(person.name)", {"person": {"name": "adam"}}) == "ADAM"
    )
    assert (
        evaluator.evaluate(
            "CONCAT(person.name, person.birthplace.street)",
            {"person": {"name": "asim", "birthplace": {"street": "surrey"}}},
        )
        == "asimsurrey"
    )


def test_evaluate_from_array(evaluator):
    assert evaluator.evaluate("UPPER(names[0])", {"names": ["adam", "eve"]}) == "ADAM"
    assert (
        evaluator.evaluate("CONCAT(names[0], names[1])", {"names": ["adam", "eve"]})
        == "adameve"
    )
    assert evaluator.evaluate("names[-1]", {"names": ["adam", "eve"]}) == "eve"
    assert (
        evaluator.evaluate("CONCAT_WS('<3', names)", {"names": ["adam", "eve"]})
        == "adam<3eve"
    )


def test_evaluate_function_chain(evaluator):
    obj = {"name": "adam", "city": {"name": "london"}}

    assert evaluator.evaluate("UPPER(CONCAT('hello', ' ', name))", obj) == "HELLO ADAM"
    assert (
        evaluator.evaluate(
            "LOWER(CONCAT(UPPER('hello'), ' ', CONCAT(LOWER(UPPER(name))), ' from ', city.name))",
            obj,
        )
        == "hello adam from london"
    )


def test_evaluate_nested(evaluator):
    obj = {
        "movies": [
            {"title": "The Dark Knight", "year": 2008},
            {
                "title": "Inception",
                "year": 2010,
                "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            },
            {
                "title": "Interstellar",
                "reviews": [
                    {"rating": 8.6, "reviewer": "IMDb"},
                    {"rating": 74, "reviewer": "Metacritic"},
                ],
            },
        ]
    }

    assert evaluator.evaluate("movies[0].title", obj) == "The Dark Knight"
    assert evaluator.evaluate("movies[1].actors[0]", obj) == "Leonardo DiCaprio"
    assert evaluator.evaluate("movies[2].reviews[0].rating", obj) == 8.6


def test_evaluate_unknown_function(evaluator):
    with pytest.raises(ValueError, match="Unknown function: UNKNOWN"):
        evaluator.evaluate("UNKNOWN(a, b, c)", {})


@pytest.mark.parametrize("expression", ["UPPER('hello'", "UPPER(lower('hello')))"])
def test_invalid_parenthesis(evaluator, expression):
    with pytest.raises(SyntaxError):
        evaluator.evaluate(expression, {})


def test_register_custom_function():
    evaluator1 = ExpressionEvaluator()
    evaluator2 = ExpressionEvaluator()

    @evaluator1.define_function("CUSTOM")
    def custom_func(a, b):
        return a + b

    assert evaluator1.evaluate("CUSTOM(a, b)", {"a": 10, "b": 20}) == 30

    with pytest.raises(ValueError, match="Unknown function: CUSTOM"):
        evaluator2.evaluate("CUSTOM(a, b)", {"a": 10, "b": 20})
