import uuid
from sqlalchemy import Column, Integer, String, Float, DateTime, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class MarketTrend(Base):
    __tablename__ = "market_trends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)

    title = Column(String, nullable=False)
    insight_type = Column(String, nullable=False)  # 'Opportunity', 'Threat', 'Efficiency Improvement'
    observation = Column(Text, nullable=False)

    # Recommendation details
    recommendation_action = Column(Text, nullable=False)
    recommendation_justification = Column(Text, nullable=False)

    # Metadata
    strength_score = Column(Float, nullable=True)  # 0.0-1.0 confidence
    category = Column(String, nullable=True)  # 'financial', 'competitor', 'legal', 'operational'

    detected_at = Column(DateTime(timezone=True), server_default=func.now())
