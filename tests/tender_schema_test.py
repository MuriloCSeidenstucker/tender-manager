from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time
from pydantic import ValidationError

from src.infra.entities import (
    ParticipationResult,
    TenderFormat,
    TenderModality,
    TenderStatus,
)
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


@freeze_time("2026-04-18 10:00:00", tz_offset=-3)
def test_should_use_brasilia_timezone_when_session_date_is_omitted():
    default_data = {
        "tender_number": 1,
        "tender_year": 2026,
        "public_body_name": "Pref",
        "modality": TenderModality.TRADING_SESSION,
        "format": TenderFormat.ELECTRONIC,
        "object_description": "Valid description",
    }

    schema = TenderCreateSchema(**default_data)

    # default datetime.now(BR_TZ) inside freeze_time will be local freezing time adjusted with the offset inside the code.
    # freezegun might have quirks with ZoneInfo. Let's make sure it's valid.
    expected_time = datetime.now(tz=ZoneInfo("America/Sao_Paulo"))
    assert schema.session_date == expected_time


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


def test_should_set_awarded_value_to_zero_when_result_is_lost():
    default_data = {
        "tender_number": 1,
        "tender_year": 2026,
        "public_body_name": "Pref",
        "modality": TenderModality.TRADING_SESSION,
        "format": TenderFormat.ELECTRONIC,
        "object_description": "Valid description",
        "participation_result": ParticipationResult.LOST,
        "awarded_value": Decimal("100.50"),
    }

    schema = TenderCreateSchema(**default_data)
    assert schema.awarded_value == Decimal("0.0")

    schema_update = TenderUpdateSchema(
        participation_result=ParticipationResult.LOST, awarded_value=Decimal("100.50")
    )
    assert schema_update.awarded_value == Decimal("0.0")


@pytest.mark.parametrize(
    "status",
    [
        TenderStatus.MONITORING,
        TenderStatus.ANALYSIS,
        TenderStatus.APPROVED,
        TenderStatus.REJECTED,
        TenderStatus.REGISTERED,
        TenderStatus.SUSPENDED,
        TenderStatus.CANCELED,
    ],
)
def test_should_raise_error_when_awarded_value_is_greater_than_zero_and_status_is_invalid(
    status,
):
    default_data = {
        "tender_number": 1,
        "tender_year": 2026,
        "public_body_name": "Pref",
        "modality": TenderModality.TRADING_SESSION,
        "format": TenderFormat.ELECTRONIC,
        "object_description": "Valid description",
        "status": status,
        "awarded_value": Decimal("100.50"),
    }

    with pytest.raises(ValidationError):
        TenderCreateSchema(**default_data)

    with pytest.raises(ValidationError):
        TenderUpdateSchema(status=status, awarded_value=Decimal("100.50"))
