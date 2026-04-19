import pytest
from pydantic import ValidationError

from src.infra.entities import ParticipationResult, TenderFormat, TenderModality
from src.schemas.tender import TenderCreateSchema, TenderUpdateSchema


def test_should_raise_error_when_object_description_is_less_than_3_characters():
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


def test_should_set_pending_result_when_participation_result_is_omitted():
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
