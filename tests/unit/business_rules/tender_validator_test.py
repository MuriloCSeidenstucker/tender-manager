from decimal import Decimal
from http import HTTPStatus

import pytest
from fastapi import HTTPException

from src.infra.entities import ParticipationResult, TenderStatus
from src.services.validators.tender_validator import TenderValidator


def test_should_raise_error_when_participation_is_lost_and_value_is_not_zero():
    with pytest.raises(HTTPException) as exc:
        TenderValidator.validate_rules(
            participation_result=ParticipationResult.LOST,
            awarded_value=Decimal("100.50"),
            status=TenderStatus.FINISHED,
        )
    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_should_raise_error_when_participation_is_won_and_value_is_zero():
    with pytest.raises(HTTPException) as exc:
        TenderValidator.validate_rules(
            participation_result=ParticipationResult.WON,
            awarded_value=Decimal("0.0"),
            status=TenderStatus.FINISHED,
        )
    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


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
def test_should_raise_error_when_value_is_greater_than_zero_but_status_is_blocked(
    status,
):
    with pytest.raises(HTTPException) as exc:
        TenderValidator.validate_rules(
            participation_result=ParticipationResult.PENDING,
            awarded_value=Decimal("100.50"),
            status=status,
        )
    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_should_pass_validation_when_data_is_correct():
    TenderValidator.validate_rules(
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("1500.00"),
        status=TenderStatus.FINISHED,
    )
