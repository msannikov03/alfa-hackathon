from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.services.competitor_service import competitor_service
from app.api.auth import get_current_user_optional

router = APIRouter()

# Pydantic models
class CompetitorCreate(BaseModel):
    name: str
    website_url: Optional[str] = None
    vk_group_id: Optional[str] = None
    telegram_channel: Optional[str] = None

class Competitor(BaseModel):
    id: UUID
    user_id: int
    name: str
    website_url: Optional[str] = None
    vk_group_id: Optional[str] = None
    telegram_channel: Optional[str] = None
    last_scanned: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CompetitorAction(BaseModel):
    id: UUID
    competitor_id: UUID
    action_type: str
    details: Dict[str, Any]
    detected_at: datetime

    class Config:
        from_attributes = True 

@router.post("/", response_model=Competitor)
async def create_competitor(
    competitor_in: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Add a new competitor."""
    return await competitor_service.create(db=db, user_id=user_id, competitor_in=competitor_in.dict())

@router.get("/", response_model=List[Competitor])
async def list_competitors(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """List all competitors."""
    return await competitor_service.get_all(db=db, user_id=user_id)

@router.get("/{competitor_id}", response_model=Competitor)
async def get_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Get a specific competitor by ID."""
    competitor = await competitor_service.get(db=db, competitor_id=competitor_id, user_id=user_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return competitor

@router.delete("/{competitor_id}", status_code=204)
async def delete_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Delete a competitor."""
    success = await competitor_service.delete(db=db, competitor_id=competitor_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return

@router.get("/{competitor_id}/actions", response_model=List[CompetitorAction])
async def get_competitor_actions(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Get recent actions for a specific competitor."""
    return await competitor_service.get_actions(db=db, competitor_id=competitor_id, user_id=user_id)

@router.post("/{competitor_id}/scan", response_model=dict)
async def force_scan_competitor(
    competitor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Manually trigger a scan for a competitor."""
    result = await competitor_service.scan_competitor(db=db, competitor_id=competitor_id, user_id=user_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/insights", response_model=dict)
async def get_competitor_insights(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Get analysis and insights about competitors."""
    return await competitor_service.get_insights(db=db, user_id=user_id)
