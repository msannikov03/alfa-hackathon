import json
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
import pandas as pd

from app.models import FinancialTransaction, CompetitorAction, LegalUpdate
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class TrendsService:

    async def identify_trends(self, db: AsyncSession, user_id: int) -> Dict:
        logger.info(f"Starting trend analysis for user {user_id}")
        
        # 1. --- Enhanced Data Preparation ---
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Financial Summary
        fin_trans_result = await db.execute(
            select(FinancialTransaction)
            .where(FinancialTransaction.user_id == user_id, FinancialTransaction.date >= thirty_days_ago)
        )
        transactions = fin_trans_result.scalars().all()
        
        financial_dossier = {"error": "Not enough data"}
        if transactions:
            df = pd.DataFrame([(t.date, t.amount, t.description) for t in transactions], columns=['date', 'amount', 'description'])
            df['amount'] = pd.to_numeric(df['amount'])
            
            total_profit = df['amount'].sum()
            
            revenue_df = df[df['amount'] > 0].groupby('description')['amount'].agg(['sum', 'count']).nlargest(5, 'sum')
            expense_df = df[df['amount'] < 0].groupby('description')['amount'].agg(['sum', 'count']).nsmallest(5, 'sum')

            financial_dossier = {
                "overall_profit_trend": f"{total_profit:+.2f}",
                "top_revenue_categories": revenue_df.reset_index().rename(columns={'sum': 'revenue', 'count': 'transactions'}).to_dict('records'),
                "top_expense_categories": expense_df.reset_index().rename(columns={'sum': 'expense', 'count': 'transactions'}).to_dict('records'),
            }

        # Competitor Summary
        comp_actions_result = await db.execute(
            select(CompetitorAction)
            .join(CompetitorAction.competitor)
            .where(Competitor.user_id == user_id, CompetitorAction.detected_at >= thirty_days_ago)
        )
        competitor_actions = [{"competitor": r.competitor.name, "action": r.details} for r in comp_actions_result.scalars().all()]

        # Legal Summary
        legal_updates_result = await db.execute(
            select(LegalUpdate.impact_level, LegalUpdate.title)
            .where(LegalUpdate.user_id == user_id, LegalUpdate.detected_at >= thirty_days_ago)
        )
        legal_updates = [{"impact": r.impact_level, "title": r.title} for r in legal_updates_result.all()]

        # 2. --- Construct the "Mega-Prompt" ---
        prompt = self._build_consultant_prompt(financial_dossier, competitor_actions, legal_updates)
        
        # 3. --- Call LLM ---
        response_str = await llm_service._call_llm([{"role": "user", "content": prompt}])
        
        try:
            trends = json.loads(response_str)
            return trends
        except json.JSONDecodeError:
            logger.error(f"Failed to decode trends JSON from LLM: {response_str}")
            return {"error": "Failed to generate trends from AI."}

    def _build_consultant_prompt(self, financials: Dict, competitors: List, legals: List) -> str:
        # This prompt is structured exactly as designed in the planning phase.
        return f"""
[SYSTEM] Persona:
You are "SYNAPSE", an elite AI business strategist from a top-tier consulting firm. You are analytical, data-driven, and relentlessly focused on providing clients with specific, high-impact, and actionable advice. You never give vague recommendations. You think in terms of opportunities, threats, and quantifiable outcomes. Your reputation is built on turning raw data into strategic gold.

[USER] Task & Context:
Client: A small business owner.
Objective: Analyze the provided data streams from the last 30 days to identify the 3 most critical strategic insights.

Here is the client's data dossier:

1. Internal Financials:
{json.dumps(financials, indent=2, ensure_ascii=False)}

2. Competitor Landscape:
{json.dumps(competitors, indent=2, ensure_ascii=False)}

3. Market & Regulatory Environment:
{json.dumps(legals, indent=2, ensure_ascii=False)}

Your Mandate:
Based *only* on the data provided, produce a JSON array of exactly 3 strategic insights. For each insight, you must provide the following structure:

```json
[
  {{
    "insight_type": "Opportunity" | "Threat" | "Efficiency Improvement",
    "title": "A concise, impactful headline for the insight.",
    "observation": "Your core analysis. Connect at least two different data points from the dossier to support your conclusion. Be specific. Example: 'Competitor X's promotion directly targets your highest-volume product category, while your marketing expenses have remained flat.'",
    "recommendation": {{
      "action": "A highly specific, concrete next step. Instead of 'improve marketing', say 'Reallocate 10,000 from the 'General Supplies' budget to run targeted social media ads for your 'Pastries' category, which has high margins but lower volume.'",
      "justification": "The 'why' behind your action. Explain the expected outcome with numbers if possible. Example: 'This aims to boost pastry sales by 20% and counter the competitor's move without engaging in a price war on your core coffee products.'"
    }}
  }}
]
```

Crucial Directives:
- No Generic Advice: Do not suggest "improving sales" or "watching competitors." Be specific.
- Data-Driven: Every observation must be explicitly tied to the data provided in the dossier.
- Quantify: Use numbers from the dossier to justify your recommendations whenever possible.
- Prioritize: Identify the *most important* 3 insights, not just everything you see.

Failure to adhere to this structure and level of detail will result in a failed analysis. Proceed.
"""

trends_service = TrendsService()

# Need to import Competitor for the join
from app.models import Competitor
