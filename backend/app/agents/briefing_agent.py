from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Briefing, AutonomousAction, BusinessContext, User
from app.services.llm_service import llm_service
from app.config import settings

logger = logging.getLogger(__name__)


class BriefingAgent:
    """Agent for generating and delivering morning briefings"""

    async def generate_daily_briefing(self, user_id: int) -> Dict[str, Any]:
        """Generate a comprehensive daily briefing for a user"""
        try:
            async with AsyncSessionLocal() as session:
                # Get business context
                business_context = await self._get_business_context(session, user_id)

                # Get recent actions (last 24 hours)
                recent_actions = await self._get_recent_actions(session, user_id)

                # Calculate metrics
                metrics = await self._calculate_metrics(session, user_id, recent_actions)

                # Generate briefing using LLM
                briefing_content = await llm_service.generate_briefing(
                    business_context=business_context,
                    recent_actions=recent_actions,
                    metrics=metrics,
                )

                # Store briefing in database
                await self._store_briefing(session, user_id, briefing_content)

                return briefing_content
        except Exception as e:
            logger.error(f"Error generating briefing for user {user_id}: {e}")
            return self._get_fallback_briefing()

    async def _get_business_context(self, session: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Retrieve business context for a user"""
        try:
            result = await session.execute(
                select(BusinessContext).where(BusinessContext.user_id == user_id)
            )
            context = result.scalar_one_or_none()

            if context:
                return {
                    "business_name": context.business_name,
                    "business_type": context.business_type,
                    "location": context.location,
                    "operating_hours": context.operating_hours,
                    "average_daily_revenue": context.average_daily_revenue,
                    "typical_customer_count": context.typical_customer_count,
                    "employee_count": context.employee_count,
                    "key_metrics": context.key_metrics,
                    "decision_thresholds": context.decision_thresholds,
                }
            else:
                return self._get_default_context()
        except Exception as e:
            logger.error(f"Error getting business context: {e}")
            return self._get_default_context()

    def _get_default_context(self) -> Dict[str, Any]:
        """Return default business context"""
        return {
            "business_name": "Your Business",
            "business_type": "general",
            "location": "Not set",
            "operating_hours": {"open": "09:00", "close": "18:00"},
            "average_daily_revenue": 50000,
            "typical_customer_count": 100,
            "employee_count": 5,
            "key_metrics": {},
            "decision_thresholds": {
                "auto_approve": {"max_amount": 10000},
                "require_approval": {"amount_range": [10000, 50000]},
                "always_escalate": {"min_amount": 50000},
            },
        }

    async def _get_recent_actions(self, session: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
        """Get actions from the last 24 hours"""
        try:
            yesterday = datetime.now() - timedelta(days=1)

            result = await session.execute(
                select(AutonomousAction)
                .where(AutonomousAction.user_id == user_id)
                .where(AutonomousAction.executed_at >= yesterday)
                .order_by(AutonomousAction.executed_at.desc())
            )
            actions = result.scalars().all()

            return [
                {
                    "action": action.action_type,
                    "description": action.description,
                    "time": action.executed_at.strftime("%H:%M"),
                    "impact_amount": action.impact_amount,
                    "required_approval": action.required_approval,
                }
                for action in actions
            ]
        except Exception as e:
            logger.error(f"Error getting recent actions: {e}")
            return []

    async def _calculate_metrics(
        self,
        session: AsyncSession,
        user_id: int,
        recent_actions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calculate performance metrics"""
        try:
            # In a real implementation, this would pull from actual business data
            # For now, we'll generate sample metrics

            # Count actions by type
            action_count = len(recent_actions)
            financial_actions = sum(1 for a in recent_actions if "financial" in a.get("action", ""))

            # Sample metrics (would be real in production)
            return {
                "yesterday_revenue": 67500,
                "customer_count": 142,
                "comparison_percent": "+12%",
                "actions_completed": action_count,
                "financial_actions": financial_actions,
                "time_saved_hours": round(action_count * 0.25, 1),  # Estimate 15 min per action
            }
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {
                "yesterday_revenue": 0,
                "customer_count": 0,
                "comparison_percent": "0%",
                "actions_completed": 0,
                "financial_actions": 0,
                "time_saved_hours": 0,
            }

    async def _store_briefing(
        self,
        session: AsyncSession,
        user_id: int,
        content: Dict[str, Any],
    ) -> bool:
        """Store briefing in database"""
        try:
            briefing = Briefing(
                user_id=user_id,
                date=datetime.now().date(),
                content=content,
                delivered=False,
            )

            session.add(briefing)
            await session.commit()

            logger.info(f"Briefing stored for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing briefing: {e}")
            await session.rollback()
            return False

    def _get_fallback_briefing(self) -> Dict[str, Any]:
        """Return a fallback briefing when generation fails"""
        return {
            "summary": "Доброе утро! К сожалению, произошла ошибка при генерации брифинга. Пожалуйста, попробуйте позже.",
            "completed_actions": [],
            "metrics": {
                "yesterday_revenue": 0,
                "customer_count": 0,
                "comparison_percent": "0%",
            },
        }

    async def generate_all_briefings(self):
        """Generate briefings for all active users"""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User))
                users = result.scalars().all()

                logger.info(f"Generating briefings for {len(users)} users")

                for user in users:
                    try:
                        await self.generate_daily_briefing(user.id)
                    except Exception as e:
                        logger.error(f"Error generating briefing for user {user.id}: {e}")

                logger.info("All briefings generated successfully")
        except Exception as e:
            logger.error(f"Error in generate_all_briefings: {e}")


# Singleton instance
briefing_agent = BriefingAgent()
