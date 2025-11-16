from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional
from uuid import UUID
import json
import logging

from app.models import Competitor, CompetitorAction
from app.schemas import CompetitorCreate
from app.services.llm_service import llm_service
from app.services.scraping_service import scraping_service

logger = logging.getLogger(__name__)

class CompetitorService:
    async def get(self, db: AsyncSession, competitor_id: UUID, user_id: int) -> Optional[Competitor]:
        result = await db.execute(
            select(Competitor).where(Competitor.id == competitor_id, Competitor.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, user_id: int) -> List[Competitor]:
        result = await db.execute(
            select(Competitor).where(Competitor.user_id == user_id).order_by(Competitor.name)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, user_id: int, competitor_in: CompetitorCreate) -> Competitor:
        new_competitor = Competitor(**competitor_in.dict(), user_id=user_id)
        db.add(new_competitor)
        await db.commit()
        await db.refresh(new_competitor)
        return new_competitor

    async def delete(self, db: AsyncSession, competitor_id: UUID, user_id: int) -> bool:
        competitor = await self.get(db, competitor_id, user_id)
        if not competitor:
            return False
        await db.execute(delete(CompetitorAction).where(CompetitorAction.competitor_id == competitor_id))
        await db.delete(competitor)
        await db.commit()
        return True

    async def get_actions(self, db: AsyncSession, competitor_id: UUID, user_id: int) -> List[CompetitorAction]:
        competitor = await self.get(db, competitor_id, user_id)
        if not competitor:
            return []
        result = await db.execute(
            select(CompetitorAction)
            .where(CompetitorAction.competitor_id == competitor_id)
            .order_by(CompetitorAction.detected_at.desc())
            .limit(50)
        )
        return result.scalars().all()

    async def scan_competitor(self, db: AsyncSession, competitor_id: UUID, user_id: int) -> dict:
        competitor = await self.get(db, competitor_id, user_id)
        if not competitor or not competitor.website_url:
            return {"error": "Competitor not found or has no URL"}

        # 1. Scrape the content from the URL
        logger.info(f"Scraping URL: {competitor.website_url}")
        content = await scraping_service.fetch_url_content(competitor.website_url)
        if not content:
            return {"error": "Failed to fetch content from URL"}
        
        # Truncate content to avoid exceeding LLM token limits
        content = content[:12000]

        # 2. Use LLM to analyze the data
        prompt = f"""
        Analyze the following text scraped from the website of a competitor named '{competitor.name}'.
        Identify any promotions, price changes, or new products.
        Respond in a structured JSON format. If nothing is found, return an empty list [].
        
        JSON format:
        [
          {{
            "action_type": "price_change" | "new_promotion" | "new_product",
            "details": {{
              "title": "A short title for the action/product",
              "description": "A detailed description, including discount size, conditions, product name, etc."
            }}
          }}
        ]

        Text to analyze:
        ---
        {content}
        ---
        """
        
        messages = [{"role": "user", "content": prompt}]
        llm_response_str = await llm_service._call_llm(messages)

        # 3. Parse the response and save actions
        try:
            actions = json.loads(llm_response_str)
            if not isinstance(actions, list):
                logger.error("LLM returned non-list data for competitor scan")
                return {"status": "Scan completed", "found_actions": 0, "details": "LLM returned non-list data"}

            for action_data in actions:
                new_action = CompetitorAction(
                    competitor_id=competitor_id,
                    action_type=action_data.get("action_type"),
                    details=action_data.get("details"),
                )
                db.add(new_action)
            
            if actions:
                await db.commit()
            return {"status": "Scan completed", "found_actions": len(actions)}

        except json.JSONDecodeError:
            logger.error(f"Failed to decode LLM JSON response: {llm_response_str}")
            return {"status": "Scan failed", "details": "Failed to decode LLM response"}
        except Exception as e:
            logger.error(f"Error saving competitor actions: {e}")
            return {"status": "Scan failed", "details": str(e)}

    async def get_insights(self, db: AsyncSession, user_id: int) -> dict:
        # This method can be implemented later, for now, it's a placeholder
        return {
            "summary": "Анализ инсайтов находится в разработке.",
            "key_findings": [],
            "recommendations": []
        }

competitor_service = CompetitorService()
