from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import logging

from app.models import Competitor, CompetitorAction
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

    async def create(self, db: AsyncSession, user_id: int, competitor_in: Dict[str, Any]) -> Competitor:
        new_competitor = Competitor(**competitor_in, user_id=user_id)
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
        if not competitor:
            return {"error": "Конкурент не найден", "error_type": "not_found"}

        content_parts = []
        errors = []

        # 1. Scrape website content if URL exists
        if competitor.website_url:
            logger.info(f"Scraping website: {competitor.website_url}")
            website_result = await scraping_service.fetch_url_content(competitor.website_url)
            if website_result["success"]:
                content_parts.append(f"=== Website Content ===\n{website_result['content'][:6000]}")
            else:
                errors.append(f"Сайт: {website_result['error']}")

        # 2. Scrape Telegram channel if specified
        if competitor.telegram_channel:
            logger.info(f"Scraping Telegram channel: {competitor.telegram_channel}")
            telegram_result = await scraping_service.fetch_telegram_channel_content(competitor.telegram_channel)
            if telegram_result["success"]:
                content_parts.append(f"=== Telegram Channel Posts ===\n{telegram_result['content'][:6000]}")
            else:
                errors.append(f"Telegram: {telegram_result['error']}")

        # 3. Check if we have any content
        if not content_parts:
            error_details = "; ".join(errors) if errors else "Не удалось получить данные ни из одного источника"
            return {
                "error": f"Не удалось проанализировать конкурента. {error_details}",
                "error_type": "scraping_failed",
                "details": errors
            }

        content = "\n\n".join(content_parts)[:12000]

        # Update last_scanned timestamp
        from datetime import datetime
        competitor.last_scanned = datetime.now()

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
                await db.commit()  # Commit the last_scanned update
                return {
                    "success": True,
                    "actions": [],
                    "found_actions": 0,
                    "message": "Сканирование завершено, изменений не обнаружено"
                }

            for action_data in actions:
                new_action = CompetitorAction(
                    competitor_id=competitor_id,
                    action_type=action_data.get("action_type"),
                    details=action_data.get("details"),
                )
                db.add(new_action)

            await db.commit()
            return {
                "success": True,
                "actions": actions,
                "found_actions": len(actions),
                "message": f"Найдено {len(actions)} изменений" if actions else "Изменений не обнаружено"
            }

        except json.JSONDecodeError:
            logger.error(f"Failed to decode LLM JSON response: {llm_response_str}")
            await db.commit()  # Commit the last_scanned update
            return {
                "success": False,
                "error": "Ошибка при анализе AI",
                "error_type": "llm_parse_error"
            }
        except Exception as e:
            logger.error(f"Error saving competitor actions: {e}")
            await db.rollback()
            return {
                "success": False,
                "error": f"Ошибка при сохранении результатов: {str(e)}",
                "error_type": "database_error"
            }

    async def get_insights(self, db: AsyncSession, user_id: int) -> dict:
        # This method can be implemented later, for now, it's a placeholder
        return {
            "summary": "Анализ инсайтов находится в разработке.",
            "key_findings": [],
            "recommendations": []
        }

competitor_service = CompetitorService()
