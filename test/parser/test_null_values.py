from typing import Any,Dict
import pytest
from harambe.parser.schemas import Schemas as schemas
from harambe.parser.parser import PydanticSchemaParser, SchemaValidationError

@pytest.mark.parametrize(
    "schema, data, should_raise_error",
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
            True, 
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
            True,
        ),
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
            False, 
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
                "procurement_items": [{"code_type": "", "code": "", "code_description": "", "description": ""}],  
            },
            True,  
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
                "procurement_items": [{"code_type": "", "code": "", "code_description": "", "description": ""}], 
            },
            False, 
        ),
    ],
)
def test_pydantic_schema_validator_error(schema: Dict[str, Any], data: Dict[str, Any], should_raise_error: bool) -> None:
    validator = PydanticSchemaParser(schema)
    if should_raise_error:
        with pytest.raises(SchemaValidationError):
            validator.validate(data, base_url="http://example.com")
    else:
        try:
            validator.validate(data, base_url="http://example.com")
        except SchemaValidationError:
            pytest.fail("SchemaValidationError raised unexpectedly!")
