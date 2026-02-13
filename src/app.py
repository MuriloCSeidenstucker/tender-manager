from http import HTTPStatus

from fastapi import FastAPI

from src.presentation.schemas.user_schema import Message
from src.routers import auth, users

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Hello World!"}
