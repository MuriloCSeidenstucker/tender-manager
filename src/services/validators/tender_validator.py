from decimal import Decimal
from http import HTTPStatus

from fastapi import HTTPException

from src.infra.entities import ParticipationResult, TenderStatus


class TenderValidator:
    """
    Handles business domain rules for Tenders to ensure data consistency
    and policy compliance.
    """

    BLOCKED_STATUSES_FOR_VALUE = {
        TenderStatus.MONITORING,
        TenderStatus.ANALYSIS,
        TenderStatus.APPROVED,
        TenderStatus.REJECTED,
        TenderStatus.REGISTERED,
        TenderStatus.SUSPENDED,
        TenderStatus.CANCELED,
    }

    @staticmethod
    def validate_rules(
        participation_result: ParticipationResult | None,
        awarded_value: Decimal | None,
        status: TenderStatus | None,
    ) -> None:
        """
        Validates business rules for awarded value, result and status.
        """
        # Rule: If LOST, awarded_value must be 0
        if participation_result == ParticipationResult.LOST:
            if awarded_value is not None and awarded_value != Decimal("0.0"):
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail="Awarded value must be zero when participation result is LOST.",
                )

        # Rule: If WON, awarded_value must be > 0
        if participation_result == ParticipationResult.WON:
            if awarded_value is None or awarded_value <= 0:
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail="Awarded value must be greater than zero when participation result is WON.",
                )

        # Rule: If awarded_value > 0, check for blocked statuses
        if awarded_value is not None and awarded_value > 0:
            if status in TenderValidator.BLOCKED_STATUSES_FOR_VALUE:
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail=f"Value cannot be greater than zero for status: {status.value}",
                )
