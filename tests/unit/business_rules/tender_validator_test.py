from decimal import Decimal
from http import HTTPStatus

import pytest
from fastapi import HTTPException

from src.infra.entities import ParticipationResult, TenderStatus
from src.services.validators.tender_validator import TenderValidator


def test_tender_validator_lost_tender_with_positive_value_raises_unprocessable():
    with pytest.raises(HTTPException) as exc:
        TenderValidator.validate_rules(
            participation_result=ParticipationResult.LOST,
            awarded_value=Decimal("100.50"),
            status=TenderStatus.FINISHED,
        )
    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_tender_validator_won_tender_with_zero_value_raises_unprocessable():
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
def test_tender_validator_positive_value_with_invalid_status_raises_unprocessable(
    status,
):
    with pytest.raises(HTTPException) as exc:
        TenderValidator.validate_rules(
            participation_result=ParticipationResult.PENDING,
            awarded_value=Decimal("100.50"),
            status=status,
        )
    assert exc.value.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_tender_validator_valid_data_passes_validation():
    TenderValidator.validate_rules(
        participation_result=ParticipationResult.WON,
        awarded_value=Decimal("1500.00"),
        status=TenderStatus.FINISHED,
    )
