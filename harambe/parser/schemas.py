class Schemas:
    regulation_documents = {
        "title": {
            "type": "string",
        },
        "document_url": {
            "type": "string",
        },
    }
    government_contracts = {
        "id": {
            "type": "string",
        },
        "title": {
            "type": "string",
        },
        "status": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "location": {
            "type": "string",
        },
        "type": {
            "type": "string",
        },
        "category": {
            "type": "string",
        },
        "posted_date": {
            "type": "string",
        },
        "due_date": {
            "type": "string",
        },
        "buyer_name": {
            "type": "string",
        },
        "buyer_contact_name": {
            "type": "string",
        },
        "buyer_contact_email": {
            "type": "string",
        },
        "buyer_contact_number": {
            "type": "string",
        },
        "attachments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"title": {"type": "string"}, "url": {"type": "string"}},
            },
        },
        "procurement_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code_type": {"type": "string"},
                    "code": {"type": "string"},
                    "code_description": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
        },
    }

    government_contracts_small = {
        "id": {
            "type": "string",
            "required": True,
        },
        "title": {
            "type": "string",
            "required": True,
        },
        "description": {
            "type": "string",
        },
        "location": {
            "type": "string",
        },
        "type": {
            "type": "string",
        },
        "category": {
            "type": "string",
        },
        "posted_date": {
            "type": "string",
        },
        "due_date": {
            "type": "string",
        },
        "agency": {
            "type": "string",
        },
        "contact_name": {
            "type": "string",
        },
        "contact_email": {
            "type": "string",
        },
        "contact_number": {
            "type": "string",
        },
        "attachments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "url", "required": True},
                },
            },
        },
    }

    school_directory = {
        "first_name": {
            "type": "string",
        },
        "last_name": {
            "type": "string",
        },
        "email": {
            "type": "string",
        },
        "phone_number": {
            "type": "string",
        },
        "title": {
            "type": "string",
        },
    }
    government_meetings = {
        "title": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "classification": {
            "type": "string",
        },
        "is_cancelled": {
            "type": "boolean",
        },
        "start_time": {
            "type": "datetime",
        },
        "end_time": {
            "type": "datetime",
        },
        "is_all_day_event": {
            "type": "boolean",
        },
        "time_notes": {
            "type": "string",
        },
        "location": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "address": {
                    "type": "string",
                },
            },
        },
        "links": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                    },
                    "url": {
                        "type": "url",
                    },
                },
            },
        },
    }
