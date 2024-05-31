document_schema = {
    "title": {"type": "string", "description": "The name of the document"},
    "document_url": {
        "type": "url",
        "actions": {"download": True},
        "description": "A link to the document",
    },
}

documents_schema = {
    "documents": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The name of the document"},
                "document_url": {
                    "type": "url",
                    "description": "A link to the document",
                },
            },
        },
    }
}

contact_schema = {
    "name": {
        "type": "object",
        "properties": {
            "first_name": {
                "type": "string",
                "description": "The first name of the contact",
            },
            "last_name": {
                "type": "string",
                "description": "The last name of the contact",
            },
        },
    },
    "address": {
        "type": "object",
        "properties": {
            "street": {"type": "string", "description": "The street of the address"},
            "city": {"type": "string", "description": "The city of the address"},
            "zip": {"type": "int", "description": "The zip code of the address"},
        },
    },
    "phone_numbers": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "number": {"type": "phone_number"},
            },
        },
    },
}

# Schema with a list of strings
list_of_strings_schema = {"tags": {"type": "array", "items": {"type": "string"}}}

# Schema with a list of objects
list_of_objects_schema = {
    "users": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}},
        },
    }
}

# Schema for an object that contains a list
object_with_list_schema = {
    "team": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "members": {"type": "array", "items": {"type": "string"}},
        },
    }
}

# Schema for a list of lists
list_of_lists_schema = {
    "matrix": {"type": "array", "items": {"type": "array", "items": {"type": "int"}}}
}

# Schema for lists with nested object items that have their own lists
nested_lists_and_objects_schema = {
    "departments": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "teams": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "team_name": {"type": "string"},
                            "members": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
            },
        },
    }
}

# Schema that contains enums
enums_schema = {
    "season": {
        "type": "enum",
        "variants": [
            "winter",
            "spring",
            "summer",
            "fall",
        ],
    },
}

# Schema that uses a non-existing type
non_existing_type_schema = {
    "title": {
        "type": "this_type_does_not_exist",
        "description": "Purely to cause error in the test",
    },
}
