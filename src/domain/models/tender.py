from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TenderStatus(Enum):
    PLANNED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    CANCELLED = 4
    SUSPENDED = 5


class TenderType(Enum):
    OPEN_COMPETITION = 1
    REVERSE_AUCTION = 2
    AUCTION = 3
    COMPETITIVE_DIALOGUE = 4
    DESIGN_CONTEST = 5
    REQUEST_FOR_QUOTATION = 6
    PUBLIC_CALL = 7


class TenderFormat(Enum):
    ELECTRONIC = 1
    IN_PERSON = 2


@dataclass
class Tender:
    tender_number: int
    tender_year: int
    tender_type: TenderType
    tender_format: TenderFormat
    # public_body: PublicBody
    status = TenderStatus
    tender_object = Optional[str]
    session_date = Optional[datetime]
    awarded_value = Optional[float]
