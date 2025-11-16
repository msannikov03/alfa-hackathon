from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, List, Any
from uuid import UUID
from datetime import datetime
import csv
import io
import json
import logging

from app.database import get_db
from app.services.finance_service import finance_service
from app.api.auth import get_current_user_optional

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models
class CashFlowPrediction(BaseModel):
    id: UUID
    user_id: int
    predicted_data: List[Dict[str, Any]]
    insights: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/upload-csv")
async def get_csv_mapping(
    file: UploadFile = File(...)
):
    """
    Uploads a CSV file, and uses an LLM to determine the column mapping.
    Returns the proposed mapping for user confirmation.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")
    
    try:
        content = await file.read()
        # Decode to handle headers and sample rows
        content_str = content.decode('utf-8')
        reader = csv.reader(io.StringIO(content_str))
        headers = next(reader)
        sample_rows = [next(reader) for _ in range(min(3, len(list(reader))))]

        mapping = await finance_service.get_column_mapping_from_llm(headers, sample_rows)
        return {"mapping": mapping, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {e}")

@router.post("/forecast")
async def create_forecast_from_csv(
    current_balance: float = Form(...),
    mapping: str = Form(...), # JSON string of the mapping
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """
    Takes the uploaded file and the confirmed mapping, stores the transactions,
    and generates a new 7-day cash flow forecast.
    """
    try:
        mapping_dict = json.loads(mapping)
        content = await file.read()

        # Store transactions
        await finance_service.store_transactions_from_csv(db, user_id, content, mapping_dict)

        # Create forecast
        result = await finance_service.create_forecast(db, user_id, current_balance)
        return result

    except Exception as e:
        logger.error(f"Error creating forecast: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create forecast: {e}")


@router.get("/forecast", response_model=CashFlowPrediction)
async def get_latest_forecast(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_optional),
):
    """
    Retrieves the latest cash flow forecast for the user.
    """
    forecast = await finance_service.get_latest_forecast(db, user_id)
    if not forecast:
        raise HTTPException(status_code=404, detail="No forecast found. Please upload data and generate one.")
    return forecast
