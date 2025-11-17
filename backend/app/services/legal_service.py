import asyncio
import json
import logging
import numpy as np
import feedparser
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sentence_transformers import SentenceTransformer

from app.models import BusinessContext, LegalUpdate, ProcessedArticle, User, ComplianceAlert
from app.services.llm_service import llm_service
from app.services.scraping_service import scraping_service
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# It's better to load the model once and reuse it.
# Using a smaller, faster model for this task.
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Hardcoded list of sources for now. This should be in a config.
LEGAL_NEWS_SOURCES = [
    "https://www.garant.ru/hotlaw/rss/",
    "https://www.consultant.ru/rss/hotdocs.xml"
]

class LegalService:

    async def get_business_context(self, db: AsyncSession, user_id: int) -> BusinessContext | None:
        result = await db.execute(select(BusinessContext).where(BusinessContext.user_id == user_id))
        return result.scalar_one_or_none()

    async def update_business_context(self, db: AsyncSession, user_id: int, description: str) -> BusinessContext | None:
        # 1. Use LLM to structure the description
        prompt = f"""
        Extract structured information from the user's business description.
        Respond in a structured JSON format.

        JSON format:
        {{
          "industry": "...",
          "business_type": "...",
          "legal_form": "...",
          "location": "...",
          "keywords": ["...", "..."]
        }}

        Description: "{description}"
        """
        structured_data_str = await llm_service._call_llm([{"role": "user", "content": prompt}])
        try:
            structured_data = json.loads(structured_data_str)
        except json.JSONDecodeError:
            logger.error("Failed to decode structured data from LLM")
            return None

        # 2. Generate embedding for the structured context
        context_string = ", ".join(f"{k}: {v}" for k, v in structured_data.items())
        embedding = embedding_model.encode(context_string).tolist()

        # 3. Save to DB
        context = await self.get_business_context(db, user_id)
        if not context:
            context = BusinessContext(user_id=user_id)
            db.add(context)
        
        context.raw_description = description
        context.structured_data = structured_data
        context.embedding = [str(e) for e in embedding] # Storing as string array
        
        await db.commit()
        await db.refresh(context)
        return context

    async def daily_scan_and_process(self, db: AsyncSession):
        logger.info("Starting daily legal scan...")
        
        # 1. Fetch new articles
        new_articles = await self._fetch_new_articles(db)
        if not new_articles:
            logger.info("No new legal articles found.")
            return

        logger.info(f"Found {len(new_articles)} new articles to process.")

        # 2. Generate embeddings for new articles
        article_texts = [f"{a['title']} {a.get('summary', '')}" for a in new_articles]
        article_embeddings = embedding_model.encode(article_texts)

        # 3. Get all users with business contexts
        users_with_context = (await db.execute(select(BusinessContext))).scalars().all()

        # 4. Process for each user
        for context in users_with_context:
            await self._process_articles_for_user(db, context, new_articles, article_embeddings)
        
        # 5. Mark articles as processed
        for article in new_articles:
            db.add(ProcessedArticle(url=article['url']))
        await db.commit()
        
        logger.info("Daily legal scan finished.")

    async def _fetch_new_articles(self, db: AsyncSession) -> List[Dict]:
        """Fetch new articles from RSS feeds using feedparser"""
        all_articles = []

        for source_url in LEGAL_NEWS_SOURCES:
            try:
                logger.info(f"Fetching RSS feed from: {source_url}")
                # feedparser.parse works with both local and remote URLs
                feed = await asyncio.to_thread(feedparser.parse, source_url)

                if feed.bozo and feed.bozo_exception:
                    logger.warning(f"Error parsing RSS feed {source_url}: {feed.bozo_exception}")
                    continue

                for entry in feed.entries[:20]:  # Limit to 20 most recent entries
                    article = {
                        "title": entry.get('title', 'No Title'),
                        "url": entry.get('link', entry.get('id', f"{source_url}#{hash(entry.get('title', ''))}")),
                        "source": source_url,
                        "summary": entry.get('summary', entry.get('description', ''))
                    }
                    all_articles.append(article)

                logger.info(f"Fetched {len(feed.entries)} articles from {source_url}")

            except Exception as e:
                logger.error(f"Error fetching RSS feed from {source_url}: {e}")
                continue

        # Deduplicate based on URL
        processed_urls = set((await db.execute(select(ProcessedArticle.url))).scalars().all())
        new_articles = [a for a in all_articles if a['url'] not in processed_urls]

        logger.info(f"Found {len(new_articles)} new articles after deduplication")
        return new_articles

    async def _process_articles_for_user(self, db: AsyncSession, context: BusinessContext, articles: List[Dict], article_embeddings: np.ndarray):
        # Skip if context has no embedding
        if not context.embedding:
            logger.warning(f"Business context for user {context.user_id} has no embedding. Skipping article processing.")
            return

        user_embedding = np.array([float(e) for e in context.embedding])
        
        # Cosine similarity
        similarities = util.cos_sim(user_embedding, article_embeddings)[0]
        
        # Get top K most similar articles
        top_k = 5
        top_indices = np.argsort(similarities)[-top_k:]

        for i in top_indices:
            if similarities[i] < 0.3: continue # Similarity threshold

            article = articles[i]
            
            # Deep analysis with LLM
            prompt = f"""
            Business Context: {context.structured_data}
            Legal Article: "{article['title']}"
            Summary: "{article.get('summary', '')}"

            Analyze if this article is relevant to the business.
            If not, respond with {{"relevant": false}}.
            If relevant, respond in this JSON format:
            {{
              "relevant": true,
              "impact_level": "High" | "Medium" | "Low",
              "category": "Tax" | "Labor Law" | "Licensing" | "Other",
              "summary": "A concise summary of what the business owner needs to know."
            }}
            """
            
            llm_response_str = await llm_service._call_llm([{"role": "user", "content": prompt}])
            try:
                analysis = json.loads(llm_response_str)
                if analysis.get("relevant"):
                    new_update = LegalUpdate(
                        user_id=context.user_id,
                        title=article['title'],
                        url=article['url'],
                        source=article['source'],
                        summary=analysis['summary'],
                        impact_level=analysis['impact_level'],
                        category=analysis['category'],
                        full_text_hash=str(hash(article.get('summary', ''))),
                        details=analysis
                    )
                    db.add(new_update)
                    await db.flush()  # Flush to get the new_update.id

                    # Create compliance alert for high and medium impact updates
                    if analysis['impact_level'] in ['High', 'Medium']:
                        # Calculate due date based on impact level
                        days_until_due = 7 if analysis['impact_level'] == 'High' else 14
                        due_date = (datetime.now() + timedelta(days=days_until_due)).date()

                        compliance_alert = ComplianceAlert(
                            user_id=context.user_id,
                            legal_update_id=new_update.id,
                            status='pending',
                            action_required=f"Review and comply with: {article['title']}",
                            due_date=due_date
                        )
                        db.add(compliance_alert)
                        logger.info(f"Created compliance alert for user {context.user_id}: {article['title']}")

            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to process LLM response for legal scan: {e}")
        
        await db.commit()

    async def get_legal_updates(self, db: AsyncSession, user_id: int) -> List[LegalUpdate]:
        result = await db.execute(
            select(LegalUpdate)
            .where(LegalUpdate.user_id == user_id)
            .order_by(LegalUpdate.detected_at.desc())
            .limit(50)
        )
        return result.scalars().all()


legal_service = LegalService()

# Need to import util from sentence_transformers
from sentence_transformers import util
