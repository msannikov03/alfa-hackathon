from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.services.legal_service import legal_service
from app.api.auth import get_current_user_optional
from app.models import ComplianceAlert as ComplianceAlertModel
from sqlalchemy import select as db_select

router = APIRouter()

# Pydantic models
class BusinessContextCreate(BaseModel):
    raw_description: str

class BusinessContext(BaseModel):
    id: int  # Changed from UUID to int to match database model
    user_id: int
    raw_description: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    embedding: Optional[List[str]] = None

    class Config:
        from_attributes = True

class LegalUpdate(BaseModel):
    id: UUID
    user_id: int
    title: str
    url: str
    source: str
    summary: str
    impact_level: str
    category: str
    full_text_hash: str
    detected_at: datetime
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

@router.post("/business-context", response_model=BusinessContext)
async def update_business_context(
    context_in: BusinessContextCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Update the user's business context."""
    context = await legal_service.update_business_context(
        db=db, user_id=user_id, description=context_in.raw_description
    )
    if not context:
        raise HTTPException(status_code=500, detail="Failed to process business context with LLM.")
    return context

@router.get("/business-context", response_model=BusinessContext)
async def get_business_context(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Get the user's current business context."""
    context = await legal_service.get_business_context(db=db, user_id=user_id)
    if not context:
        raise HTTPException(status_code=404, detail="Business context not set for this user.")
    return context

@router.get("/updates", response_model=List[LegalUpdate])
async def get_legal_updates(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """Get the latest legal updates relevant to the user."""
    return await legal_service.get_legal_updates(db=db, user_id=user_id)

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

@router.get("/compliance-alerts")
async def get_compliance_alerts(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """
    Get all compliance alerts for the user, ordered by due date.
    """
    result = await db.execute(
        db_select(ComplianceAlertModel)
        .where(ComplianceAlertModel.user_id == user_id)
        .order_by(ComplianceAlertModel.due_date.asc())
    )
    alerts = result.scalars().all()
    return [
        {
            "id": str(alert.id),
            "legal_update_id": str(alert.legal_update_id),
            "status": alert.status,
            "action_required": alert.action_required,
            "due_date": str(alert.due_date) if alert.due_date else None,
            "created_at": alert.created_at.isoformat(),
        }
        for alert in alerts
    ]

@router.post("/compliance-alerts/{alert_id}/complete")
async def complete_compliance_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """
    Mark a compliance alert as completed.
    """
    result = await db.execute(
        db_select(ComplianceAlertModel).where(
            ComplianceAlertModel.id == alert_id,
            ComplianceAlertModel.user_id == user_id
        )
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Compliance alert not found")

    alert.status = 'completed'
    alert.completed_at = datetime.now()
    await db.commit()

    return {"message": "Compliance alert marked as completed"}
