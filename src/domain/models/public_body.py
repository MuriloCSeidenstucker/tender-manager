from dataclasses import dataclass
from typing import Optional


@dataclass
class PublicBody:
    name = str
    cnpj = Optional[str]
    street_address = Optional[str]
    number_address = Optional[str]
    complement_address = Optional[str]
    district = Optional[str]
    city = Optional[str]
    state_code = Optional[str]
    cep = Optional[str]
    phone = Optional[str]
    email = Optional[str]
