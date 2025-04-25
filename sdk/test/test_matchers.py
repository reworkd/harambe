import pytest

from .matchers import assert_partial_object_in


def test_assert_partial_object_in_with_matching_object():
    collection = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    partial_obj = {"id": 1}
    assert_partial_object_in(collection, partial_obj)


def test_assert_partial_object_in_with_no_matching_object():
    collection = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    partial_obj = {"id": 3}
    with pytest.raises(AssertionError):
        assert_partial_object_in(collection, partial_obj)


def test_assert_partial_object_in_with_multiple_keys_match():
    collection = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    partial_obj = {"id": 1, "name": "Alice"}
    assert_partial_object_in(collection, partial_obj)


def test_assert_partial_object_in_with_partial_keys_mismatch():
    collection = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    partial_obj = {"id": 1, "name": "Bob"}
    with pytest.raises(AssertionError):
        assert_partial_object_in(collection, partial_obj)


def test_assert_partial_object_in_with_empty_collection():
    collection = []
    partial_obj = {"id": 1}
    with pytest.raises(AssertionError):
        assert_partial_object_in(collection, partial_obj)


def test_assert_partial_object_in_with_empty_partial_obj():
    collection = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    partial_obj = {}
    assert_partial_object_in(collection, partial_obj)


def test_assert_partial_object_in_with_non_dict_collection():
    collection = ({"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"})
    partial_obj = {"id": 1}
    assert_partial_object_in(collection, partial_obj)
