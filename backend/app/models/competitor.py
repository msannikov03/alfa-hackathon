import uuid
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    website_url = Column(String, nullable=True)
    vk_group_id = Column(String, nullable=True)
    telegram_channel = Column(String, nullable=True)

    last_scanned = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CompetitorAction(Base):
    __tablename__ = "competitor_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitors.id"), nullable=False)

    action_type = Column(String, nullable=False) # 'price_change', 'new_promotion', 'new_product'
    details = Column(JSON, nullable=False)

    detected_at = Column(DateTime(timezone=True), server_default=func.now())
