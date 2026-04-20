import pytest
from pydantic import ValidationError

from src.infra.entities import ParticipationResult, TenderFormat, TenderModality
from src.schemas.tender import TenderCreateSchema, TenderUpdateSchema


def test_tender_schema_with_short_description_raises_validation_error():
    default_data = {
        "tender_number": 1,
        "tender_year": 2026,
        "public_body_name": "Pref",
        "modality": TenderModality.TRADING_SESSION,
        "format": TenderFormat.ELECTRONIC,
    }

    with pytest.raises(ValidationError):
        TenderCreateSchema(**default_data, object_description="ab")

    with pytest.raises(ValidationError):
        TenderUpdateSchema(object_description="ab")


def test_tender_schema_with_omitted_participation_result_defaults_to_pending():
    default_data = {
        "tender_number": 1,
        "tender_year": 2026,
        "public_body_name": "Pref",
        "modality": TenderModality.TRADING_SESSION,
        "format": TenderFormat.ELECTRONIC,
        "object_description": "Valid description",
    }

    schema = TenderCreateSchema(**default_data)
    assert schema.participation_result == ParticipationResult.PENDING
