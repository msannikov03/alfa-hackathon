from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import (
    User,
    Briefing,
    AutonomousAction,
    LearnedPattern,
    Decision,
    BusinessContext,
)
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service
from app.agents.briefing_agent import briefing_agent

router = APIRouter()


# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: int


class ChatResponse(BaseModel):
    response: str
    requires_approval: bool = False
    action_type: str = "general"
    confidence: float = 0.0


class ActionCreate(BaseModel):
    action_type: str
    description: str
    impact_amount: Optional[float] = None
    required_approval: bool = False
    action_metadata: Dict[str, Any] = {}


class ActionResponse(BaseModel):
    id: int
    action_type: str
    description: Optional[str]
    impact_amount: Optional[float]
    required_approval: bool
    was_approved: Optional[bool]
    executed_at: datetime

    class Config:
        from_attributes = True


class BriefingResponse(BaseModel):
    id: int
    date: str
    content: Dict[str, Any]
    generated_at: datetime
    delivered: bool

    class Config:
        from_attributes = True


class MetricsResponse(BaseModel):
    total_actions: int
    approved_actions: int
    pending_approvals: int
    time_saved_hours: float
    automation_rate: float
    decisions_made: int


# ============ Chat Endpoints ============

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage, db: AsyncSession = Depends(get_db)):
    """Main chat endpoint for AI interactions"""
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == message.user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get business context
        result = await db.execute(
            select(BusinessContext).where(BusinessContext.user_id == message.user_id)
        )
        business_context_obj = result.scalar_one_or_none()

        business_context = {}
        if business_context_obj:
            business_context = {
                "business_name": business_context_obj.business_name,
                "business_type": business_context_obj.business_type,
                "decision_thresholds": business_context_obj.decision_thresholds,
            }

        # Process with LLM
        llm_result = await llm_service.process_with_context(
            message=message.message,
            business_context=business_context,
        )

        # Store conversation in memory
        await memory_service.store_conversation(
            user_id=message.user_id,
            user_message=message.message,
            ai_response=llm_result["response"],
            context=business_context,
        )

        return ChatResponse(
            response=llm_result["response"],
            requires_approval=llm_result["requires_approval"],
            action_type=llm_result["action_type"],
            confidence=llm_result["confidence"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


# ============ Briefing Endpoints ============

@router.get("/v1/briefing/today", response_model=BriefingResponse)
async def get_today_briefing(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get today's briefing"""
    try:
        today = datetime.now().date()
        result = await db.execute(
            select(Briefing)
            .where(Briefing.user_id == user_id)
            .where(Briefing.date == today)
        )
        briefing = result.scalar_one_or_none()

        if not briefing:
            # Generate new briefing
            content = await briefing_agent.generate_daily_briefing(user_id)
            result = await db.execute(
                select(Briefing)
                .where(Briefing.user_id == user_id)
                .where(Briefing.date == today)
            )
            briefing = result.scalar_one_or_none()

        if not briefing:
            raise HTTPException(status_code=404, detail="Briefing not found")

        return BriefingResponse(
            id=briefing.id,
            date=str(briefing.date),
            content=briefing.content,
            generated_at=briefing.generated_at,
            delivered=briefing.delivered,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting briefing: {str(e)}")


@router.post("/v1/briefing/generate")
async def generate_briefing(user_id: int, db: AsyncSession = Depends(get_db)):
    """Force generate a new briefing"""
    try:
        content = await briefing_agent.generate_daily_briefing(user_id)
        return {"status": "success", "briefing": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating briefing: {str(e)}")


@router.get("/v1/briefing/history", response_model=List[BriefingResponse])
async def get_briefing_history(
    user_id: int,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """Get past briefings"""
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        result = await db.execute(
            select(Briefing)
            .where(Briefing.user_id == user_id)
            .where(Briefing.date >= start_date)
            .order_by(Briefing.date.desc())
        )
        briefings = result.scalars().all()

        return [
            BriefingResponse(
                id=b.id,
                date=str(b.date),
                content=b.content,
                generated_at=b.generated_at,
                delivered=b.delivered,
            )
            for b in briefings
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


# ============ Autonomous Actions Endpoints ============

@router.get("/v1/actions/recent", response_model=List[ActionResponse])
async def get_recent_actions(
    user_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get recent AI actions"""
    try:
        result = await db.execute(
            select(AutonomousAction)
            .where(AutonomousAction.user_id == user_id)
            .order_by(AutonomousAction.executed_at.desc())
            .limit(limit)
        )
        actions = result.scalars().all()

        return [ActionResponse.model_validate(action) for action in actions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting actions: {str(e)}")


@router.get("/v1/actions/pending", response_model=List[ActionResponse])
async def get_pending_actions(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get actions awaiting approval"""
    try:
        result = await db.execute(
            select(AutonomousAction)
            .where(AutonomousAction.user_id == user_id)
            .where(AutonomousAction.required_approval == True)
            .where(AutonomousAction.was_approved == None)
            .order_by(AutonomousAction.executed_at.desc())
        )
        actions = result.scalars().all()

        return [ActionResponse.model_validate(action) for action in actions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pending: {str(e)}")


@router.post("/v1/actions/approve/{action_id}")
async def approve_action(action_id: int, db: AsyncSession = Depends(get_db)):
    """Approve an action"""
    try:
        result = await db.execute(
            select(AutonomousAction).where(AutonomousAction.id == action_id)
        )
        action = result.scalar_one_or_none()

        if not action:
            raise HTTPException(status_code=404, detail="Action not found")

        action.was_approved = True
        await db.commit()

        return {"status": "approved", "action_id": action_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error approving: {str(e)}")


@router.post("/v1/actions/decline/{action_id}")
async def decline_action(action_id: int, db: AsyncSession = Depends(get_db)):
    """Decline an action"""
    try:
        result = await db.execute(
            select(AutonomousAction).where(AutonomousAction.id == action_id)
        )
        action = result.scalar_one_or_none()

        if not action:
            raise HTTPException(status_code=404, detail="Action not found")

        action.was_approved = False
        await db.commit()

        return {"status": "declined", "action_id": action_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error declining: {str(e)}")


@router.post("/v1/actions/create", response_model=ActionResponse)
async def create_action(
    user_id: int,
    action: ActionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new autonomous action"""
    try:
        new_action = AutonomousAction(
            user_id=user_id,
            action_type=action.action_type,
            description=action.description,
            impact_amount=action.impact_amount,
            required_approval=action.required_approval,
            action_metadata=action.action_metadata,
        )

        db.add(new_action)
        await db.commit()
        await db.refresh(new_action)

        return ActionResponse.model_validate(new_action)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating action: {str(e)}")


# ============ Pattern Recognition Endpoints ============

@router.get("/v1/patterns/active")
async def get_active_patterns(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get currently recognized patterns"""
    try:
        result = await db.execute(
            select(LearnedPattern)
            .where(LearnedPattern.user_id == user_id)
            .where(LearnedPattern.success_rate >= 0.6)
            .order_by(LearnedPattern.success_rate.desc())
            .limit(10)
        )
        patterns = result.scalars().all()

        return {
            "patterns": [
                {
                    "id": p.id,
                    "pattern_type": p.pattern_type,
                    "recommended_action": p.recommended_action,
                    "success_rate": p.success_rate,
                    "times_used": p.times_used,
                }
                for p in patterns
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patterns: {str(e)}")


@router.post("/v1/patterns/feedback")
async def provide_pattern_feedback(
    pattern_id: int,
    success: bool,
    db: AsyncSession = Depends(get_db),
):
    """Provide feedback on a pattern"""
    try:
        result = await db.execute(
            select(LearnedPattern).where(LearnedPattern.id == pattern_id)
        )
        pattern = result.scalar_one_or_none()

        if not pattern:
            raise HTTPException(status_code=404, detail="Pattern not found")

        # Update success rate (simple moving average)
        pattern.times_used += 1
        pattern.success_rate = (
            pattern.success_rate * (pattern.times_used - 1) + (1.0 if success else 0.0)
        ) / pattern.times_used
        pattern.last_used = datetime.now()

        await db.commit()

        return {"status": "success", "new_success_rate": pattern.success_rate}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating pattern: {str(e)}")


# ============ Metrics Endpoints ============

@router.get("/v1/metrics/savings")
async def get_savings_metrics(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get time and money saved metrics"""
    try:
        # Get all actions for user
        result = await db.execute(
            select(AutonomousAction).where(AutonomousAction.user_id == user_id)
        )
        all_actions = result.scalars().all()

        # Calculate metrics
        total_actions = len(all_actions)
        time_saved_hours = total_actions * 0.25  # 15 min per action
        money_saved = sum(
            a.impact_amount for a in all_actions if a.impact_amount and a.impact_amount > 0
        )

        return {
            "total_actions": total_actions,
            "time_saved_hours": round(time_saved_hours, 1),
            "money_saved_rub": round(money_saved, 2) if money_saved else 0,
            "avg_action_value": round(money_saved / max(total_actions, 1), 2) if money_saved else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating savings: {str(e)}")


@router.get("/v1/metrics/performance", response_model=MetricsResponse)
async def get_performance_metrics(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get AI performance metrics"""
    try:
        # Get actions from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)

        result = await db.execute(
            select(AutonomousAction)
            .where(AutonomousAction.user_id == user_id)
            .where(AutonomousAction.executed_at >= thirty_days_ago)
        )
        actions = result.scalars().all()

        total_actions = len(actions)
        approved_actions = sum(1 for a in actions if a.was_approved is True)
        pending_approvals = sum(
            1 for a in actions if a.required_approval and a.was_approved is None
        )

        # Calculate automation rate
        decided_actions = total_actions - pending_approvals
        automation_rate = (
            (decided_actions / total_actions * 100) if total_actions > 0 else 0
        )

        # Time saved
        time_saved_hours = total_actions * 0.25

        # Get decision count
        result = await db.execute(
            select(Decision)
            .where(Decision.user_id == user_id)
            .where(Decision.created_at >= thirty_days_ago)
        )
        decisions = result.scalars().all()

        return MetricsResponse(
            total_actions=total_actions,
            approved_actions=approved_actions,
            pending_approvals=pending_approvals,
            time_saved_hours=round(time_saved_hours, 1),
            automation_rate=round(automation_rate, 1),
            decisions_made=len(decisions),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance: {str(e)}")


# ============ User & Business Context Endpoints ============

@router.get("/user/{user_id}")
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user business profile"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get business context
        result = await db.execute(
            select(BusinessContext).where(BusinessContext.user_id == user_id)
        )
        context = result.scalar_one_or_none()

        return {
            "user_id": user.id,
            "username": user.username,
            "business_name": context.business_name if context else None,
            "business_type": context.business_type if context else None,
            "business_context": {
                "location": context.location if context else None,
                "operating_hours": context.operating_hours if context else None,
                "employee_count": context.employee_count if context else None,
            }
            if context
            else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")


@router.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    """Telegram bot webhook"""
    # Process telegram updates (handled by bot directly in production)
    return {"ok": True}