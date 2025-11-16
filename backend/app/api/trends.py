from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from app.database import get_db
from app.services.trends_service import trends_service

router = APIRouter()

TEMP_USER_ID = 1

@router.get("/", response_model=List[Dict])
async def get_trends(
    db: AsyncSession = Depends(get_db),
):
    """
    Analyzes all available data (finance, competitors, legal)
    and returns a list of strategic trends and recommendations.
    """
    trends = await trends_service.identify_trends(db, TEMP_USER_ID)
    return trends
