from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CompanySize(Enum):
    MEI = 1
    ME = 2
    EPP = 3
    OTHER = 4


@dataclass
class Company:
    name = str
    trade_name = Optional[str]
    cnpj = str
    company_size = Optional[CompanySize]
    street_address = Optional[str]
    number_address = Optional[str]
    complement_address = Optional[str]
    district = Optional[str]
    city = Optional[str]
    state_code = Optional[str]
    cep = Optional[str]
    phone = Optional[str]
    email = Optional[str]
