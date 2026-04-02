from typing import Literal

from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    access_token: str = Field(..., min_length=1)
    token_type: Literal["bearer"]
