from typing import Collection, Any


def assert_partial_object_in(collection: Collection, partial_obj: dict[str, Any]):
    if not isinstance(collection, list):
        collection = list(collection)

    for obj in collection:
        for key, expected in partial_obj.items():
            if key not in obj or obj[key] != expected:
                break
        else:
            return

    assert False, f"Object {partial_obj} not found in {collection}"
