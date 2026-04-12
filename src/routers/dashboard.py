from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.entities import UserEntity
from src.infra.settings.database import get_session
from src.schemas.dashboard import DashboardResponseSchema
from src.security import get_current_user
from src.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserEntity, Depends(get_current_user)]


@router.get("/metrics", response_model=DashboardResponseSchema)
async def get_dashboard_metrics(
    session: Session,
    current_user: CurrentUser,
    year: int = Query(default_factory=lambda: datetime.now().year),
):
    return await DashboardService(session).get_metrics(current_user.id, year)
