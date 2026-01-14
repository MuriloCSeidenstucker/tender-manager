from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    name = str
    cpf = str
    email = Optional[str]
