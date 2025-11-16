from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas import BusinessContext, LegalUpdate, BusinessContextCreate
from app.services.legal_service import legal_service

router = APIRouter()

# Since auth is not our problem, we need a temporary way to identify a user.
# I will use a hardcoded user_id for now.
TEMP_USER_ID = 1

@router.post("/business-context", response_model=BusinessContext)
async def update_business_context(
    context_in: BusinessContextCreate,
    db: AsyncSession = Depends(get_db),
):
    """Update the user's business context."""
    context = await legal_service.update_business_context(
        db=db, user_id=TEMP_USER_ID, description=context_in.raw_description
    )
    if not context:
        raise HTTPException(status_code=500, detail="Failed to process business context with LLM.")
    return context

@router.get("/business-context", response_model=BusinessContext)
async def get_business_context(
    db: AsyncSession = Depends(get_db),
):
    """Get the user's current business context."""
    context = await legal_service.get_business_context(db=db, user_id=TEMP_USER_ID)
    if not context:
        raise HTTPException(status_code=404, detail="Business context not set for this user.")
    return context

@router.get("/updates", response_model=List[LegalUpdate])
async def get_legal_updates(
    db: AsyncSession = Depends(get_db),
):
    """Get the latest legal updates relevant to the user."""
    return await legal_service.get_legal_updates(db=db, user_id=TEMP_USER_ID)

@router.post("/scan")
async def force_scan_legal_updates(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger a scan for new legal updates.
    This runs as a background task.
    """
    background_tasks.add_task(legal_service.daily_scan_and_process, db)
    return {"message": "Legal update scan initiated in the background."}
