import asyncio
import csv
import io
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.models import FinancialTransaction, CashFlowPrediction
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class FinanceService:

    async def get_column_mapping_from_llm(self, headers: List[str], sample_rows: List[List[str]]) -> Dict:
        prompt = f"""
        A user uploaded a CSV file with financial transactions. I need to map their columns to my required format: `Date`, `Amount`, `Description`.
        The 'Amount' column must contain both income (positive) and expenses (negative). Sometimes the user provides separate columns for income and expenses.

        My required column names are: "date", "amount", "description".

        Here are the headers from the user's file: {headers}
        Here are a few sample rows: {sample_rows}

        Analyze the headers and samples and provide a JSON object with the mapping. The JSON should have the following structure:
        {{
          "date_column": "...", // The name of the user's date column
          "description_column": "...", // The name of the user's description column
          "amount_logic": {{
            "type": "single_column" | "separate_columns",
            // if single_column:
            "amount_column": "...",
            // if separate_columns:
            "income_column": "...",
            "expense_column": "..."
          }}
        }}
        Respond ONLY with the JSON object.
        """
        
        response_str = await llm_service._call_llm([{"role": "user", "content": prompt}])
        try:
            return json.loads(response_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode LLM mapping response: {response_str}")
            raise ValueError("Could not determine CSV mapping from LLM.")

    async def store_transactions_from_csv(self, db: AsyncSession, user_id: int, file_content: bytes, mapping: Dict):
        # Delete old transactions
        await db.execute(delete(FinancialTransaction).where(FinancialTransaction.user_id == user_id))

        df = pd.read_csv(io.BytesIO(file_content))
        
        # Rename columns based on mapping
        df.rename(columns={
            mapping['date_column']: 'date',
            mapping['description_column']: 'description'
        }, inplace=True)

        # Process amount
        amount_logic = mapping['amount_logic']
        if amount_logic['type'] == 'single_column':
            df['amount'] = pd.to_numeric(df[amount_logic['amount_column']], errors='coerce')
        elif amount_logic['type'] == 'separate_columns':
            income = pd.to_numeric(df[amount_logic['income_column']], errors='coerce').fillna(0)
            expense = pd.to_numeric(df[amount_logic['expense_column']], errors='coerce').fillna(0)
            df['amount'] = income - expense
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date', 'amount'], inplace=True)

        # Save to DB
        transactions = []
        for _, row in df.iterrows():
            transactions.append(
                FinancialTransaction(
                    user_id=user_id,
                    date=row['date'],
                    amount=row['amount'],
                    description=str(row['description'])
                )
            )
        db.add_all(transactions)
        await db.commit()
        return len(transactions)

    async def create_forecast(self, db: AsyncSession, user_id: int, current_balance: float) -> Dict:
        # Fetch last 90 days of transactions
        ninety_days_ago = datetime.now() - timedelta(days=90)
        result = await db.execute(
            select(FinancialTransaction)
            .where(FinancialTransaction.user_id == user_id, FinancialTransaction.date >= ninety_days_ago)
            .order_by(FinancialTransaction.date)
        )
        transactions = result.scalars().all()
        
        if not transactions:
            raise ValueError("Not enough transaction data to create a forecast.")

        df = pd.DataFrame([(t.date, t.amount, t.description) for t in transactions], columns=['date', 'amount', 'description'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # --- Smart Forecasting Logic ---
        # 1. Find recurring transactions (simplified heuristic)
        # This is a complex problem. A simple heuristic: group by description, check for regular intervals.
        # For this implementation, we will use a simpler day-of-week average model for all transactions.
        # A full implementation of recurring transaction detection is beyond the scope of a quick implementation.
        
        # 2. Calculate average volatile flow per day of week
        df['day_of_week'] = df.index.dayofweek
        daily_avg = df.groupby('day_of_week')['amount'].mean()

        # 3. Generate 7-day forecast
        prediction_dates = [datetime.now().date() + timedelta(days=i) for i in range(8)]
        predicted_balances = [current_balance]
        
        for i in range(7):
            current_date = prediction_dates[i]
            day_of_week = current_date.weekday()
            daily_change = daily_avg.get(day_of_week, 0) # Use 0 if no data for that day
            next_balance = predicted_balances[-1] + daily_change
            predicted_balances.append(next_balance)
            
        predicted_data = [{"date": d.isoformat(), "balance": b} for d, b in zip(prediction_dates, predicted_balances)]

        # 4. Get LLM Insights
        prompt = f"""
        A user's current balance is {current_balance:.2f}.
        Based on their historical transactions, here is a 7-day cash flow forecast:
        {json.dumps(predicted_data, indent=2)}

        Analyze this forecast. Identify potential risks (like days with a high chance of negative balance) and suggest simple, actionable recommendations.
        Respond in this JSON format:
        {{
          "risks": [
            {{ "severity": "High" | "Medium", "message": "..." }}
          ],
          "recommendations": [
            {{ "message": "..." }}
          ]
        }}
        If no significant risks are found, return empty lists.
        """
        insights_str = await llm_service._call_llm([{"role": "user", "content": prompt}])
        try:
            insights = json.loads(insights_str)
        except json.JSONDecodeError:
            insights = {"risks": [], "recommendations": [{"message": "Could not generate AI insights."}]}

        # 5. Save to DB
        new_prediction = CashFlowPrediction(
            user_id=user_id,
            predicted_data=predicted_data,
            insights=insights
        )
        db.add(new_prediction)
        await db.commit()
        
        return {"prediction": new_prediction}

    async def get_latest_forecast(self, db: AsyncSession, user_id: int) -> CashFlowPrediction | None:
        result = await db.execute(
            select(CashFlowPrediction)
            .where(CashFlowPrediction.user_id == user_id)
            .order_by(CashFlowPrediction.created_at.desc())
        )
        return result.scalar_one_or_none()

finance_service = FinanceService()
