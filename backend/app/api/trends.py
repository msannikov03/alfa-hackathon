from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from app.database import get_db
from app.services.trends_service import trends_service
from app.api.auth import get_current_user_optional

router = APIRouter()

@router.get("/", response_model=List[Dict])
async def get_trends(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """
    Analyzes all available data (finance, competitors, legal)
    and returns a list of strategic trends and recommendations.
    """
    trends = await trends_service.identify_trends(db, user_id)
    return trends
