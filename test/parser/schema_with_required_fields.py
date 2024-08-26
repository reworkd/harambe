document_schema = {
    "title": {
        "type": "string",
        "description": "The name of the document",
        "required": True,
    },
    "document_url": {
        "type": "url",
        "actions": {"download": True},
        "description": "A link to the document",
        "required": True,
    },
}

documents_schema = {
    "documents": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The name of the document",
                    "required": True,
                },
                "document_url": {
                    "type": "url",
                    "description": "A link to the document",
                    "required": True,
                },
            },
        },
        "required": True,
    }
}

contact_schema = {
    "name": {
        "type": "object",
        "properties": {
            "first_name": {
                "type": "string",
                "description": "The first name of the contact",
                "required": True,
            },
            "last_name": {
                "type": "string",
                "description": "The last name of the contact",
            },
        },
        "required": True,
    },
    "address": {
        "type": "object",
        "properties": {
            "street": {
                "type": "string",
                "description": "The street of the address",
            },
            "city": {
                "type": "string",
                "description": "The city of the address",
                "required": True,
            },
            "zip": {
                "type": "int",
                "description": "The zip code of the address",
            },
        },
        "required": True,
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
        "required": True,
    },
}

list_of_strings_schema = {
    "tags": {
        "type": "array",
        "items": {"type": "string"},
        "required": True,
    }
}

list_of_objects_schema = {
    "users": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "required": True},
                "email": {"type": "email"},
            },
        },
        "required": True,
    }
}

object_with_list_schema = {
    "team": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "required": True},
            "members": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": True,
    }
}

object_with_list_of_objects_schema = {
    "list": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "a": {"type": "string", "required": True},
                "b": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "c": {
                    "type": "object",
                    "properties": {
                        "d": {"type": "string", "required": True},
                        "e": {"type": "string"},
                    },
                    "required": True,
                },
            },
        },
        "required": True,
    }
}

list_of_lists_schema = {
    "matrix": {
        "type": "array",
        "items": {
            "type": "array",
            "items": {"type": "int"},
            "required": True,
        },
        "description": "A matrix of integers",
    }
}

nested_lists_and_objects_schema = {
    "departments": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "required": True},
                "teams": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "team_name": {"type": "string"},
                            "members": {
                                "type": "array",
                                "items": {"type": "string", "required": True},
                                "required": True,
                            },
                        },
                    },
                    "required": True,
                },
            },
        },
        "required": True,
    }
}

datetime_schema = {
    "event": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the event",
                "required": True,
            },
            "date": {
                "type": "datetime",
                "description": "The date of the event",
            },
        },
        "required": True,
    }
}

phone_number_schema = {
    "contact": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the contact",
                "required": True,
            },
            "phone": {
                "type": "phone_number",
                "description": "The phone number",
                "required": True,
            },
        },
        "required": True,
    }
}

url_schema = {
    "resource": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the resource",
                "required": True,
            },
            "link": {
                "type": "url",
                "description": "A link to the resource",
                "required": True,
            },
        },
        "required": True,
    }
}

object_with_nested_types_schema = {
    "profile": {
        "type": "object",
        "properties": {
            "user": {"type": "string", "description": "Username", "required": True},
            "contact": {
                "type": "phone_number",
                "description": "Contact number",
            },
            "event_date": {
                "type": "datetime",
                "description": "Event date",
            },
            "website": {
                "type": "url",
                "description": "Website URL",
            },
        },
    }
}

list_with_nested_types_schema = {
    "events": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "required": True},
                "dates": {
                    "type": "array",
                    "items": {"type": "datetime", "required": True},
                    "required": True,
                },
                "contacts": {
                    "type": "array",
                    "items": {"type": "phone_number", "required": True},
                    "required": True,
                },
                "links": {
                    "type": "array",
                    "items": {"type": "url", "required": True},
                    "required": True,
                },
            },
        },
        "required": True,
    }
}
