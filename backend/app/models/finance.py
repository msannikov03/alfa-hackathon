import uuid
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Float, nullable=False) # Positive for income, negative for expense
    description = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CashFlowPrediction(Base):
    __tablename__ = "cash_flow_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stores a list of {date, balance} for the next 7 days
    predicted_data = Column(JSON, nullable=False)
    
    # Stores the {risks, recommendations} from the LLM
    insights = Column(JSON, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
