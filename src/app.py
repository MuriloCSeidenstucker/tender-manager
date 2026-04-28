import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import auth, companies, dashboard, tenders, users
from src.schemas.common import MessageSchema
from src.settings import Settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(tenders.router)
app.include_router(dashboard.router)


@app.get("/", status_code=HTTPStatus.OK, response_model=MessageSchema)
def read_root():
    return {"message": "Hello World!"}
