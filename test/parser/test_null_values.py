from typing import Any, Dict

import pytest

from harambe.parser.parser import PydanticSchemaParser, SchemaValidationError
from harambe.parser.schemas import Schemas as schemas


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            schemas.government_contracts,
            {
                "id": None,
                "title": None,
                "status": None,
                "description": None,
                "location": None,
                "type": None,
                "category": None,
                "posted_date": None,
                "due_date": None,
                "buyer_name": None,
                "buyer_contact_name": None,
                "buyer_contact_email": None,
                "buyer_contact_number": None,
                "attachments": None,
                "procurement_items": None,
            },
        ),
        (
            schemas.government_contracts,
            {
                "id": "",
                "title": "",
                "status": "",
                "description": "",
                "location": "",
                "type": "",
                "category": "",
                "posted_date": "",
                "due_date": "",
                "buyer_name": "",
                "buyer_contact_name": "",
                "buyer_contact_email": "",
                "buyer_contact_number": "",
                "attachments": [],
                "procurement_items": [],
            },
        ),
        (
            schemas.government_contracts,
            {
                "id": "",
                "title": "",
                "status": "",
                "description": "",
                "location": "",
                "type": "",
                "category": "",
                "posted_date": "",
                "due_date": "",
                "buyer_name": "",
                "buyer_contact_name": "",
                "buyer_contact_email": "",
                "buyer_contact_number": "",
                "attachments": [{"title": "", "url": ""}],
                "procurement_items": [
                    {
                        "code_type": "",
                        "code": "",
                        "code_description": "",
                        "description": "",
                    }
                ],
            },
        ),
    ],
)
def test_pydantic_schema_validation_error_fail(
    schema: Dict[str, Any], data: Dict[str, Any]
) -> None:
    validator = PydanticSchemaParser(schema)
    with pytest.raises(SchemaValidationError):
        validator.validate(data, base_url="http://example.com")


@pytest.mark.parametrize(
    "schema, data",
    [
        (
            schemas.government_contracts,
            {
                "id": "123",
                "title": None,
                "status": None,
                "description": None,
                "location": None,
                "type": None,
                "category": None,
                "posted_date": None,
                "due_date": None,
                "buyer_name": None,
                "buyer_contact_name": None,
                "buyer_contact_email": None,
                "buyer_contact_number": None,
                "attachments": [{"title": "Attachment 1", "url": None}],
                "procurement_items": [],
            },
        ),
        (
            schemas.government_contracts,
            {
                "id": "123",
                "title": "",
                "status": "",
                "description": "",
                "location": "",
                "type": "",
                "category": "",
                "posted_date": "",
                "due_date": "",
                "buyer_name": "",
                "buyer_contact_name": "",
                "buyer_contact_email": "",
                "buyer_contact_number": "",
                "attachments": [{"title": "Attachment 1", "url": ""}],
                "procurement_items": [
                    {
                        "code_type": "",
                        "code": "",
                        "code_description": "",
                        "description": "",
                    }
                ],
            },
        ),
    ],
)
def test_pydantic_schema_validation_success(
    schema: Dict[str, Any], data: Dict[str, Any]
):
    validator = PydanticSchemaParser(schema)
    validator.validate(data, base_url="http://example.com")
