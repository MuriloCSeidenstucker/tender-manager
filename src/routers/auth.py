from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infra.entities.user_entity import UserEntity
from src.infra.settings.database import get_session
from src.presentation.schemas.user_schema import Token
from src.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session = Annotated[Session, Depends(get_session)]


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2Form, session: Session):
    user = session.scalar(
        select(UserEntity).where(UserEntity.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect email or password"
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Incorrect email or password"
        )

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}
