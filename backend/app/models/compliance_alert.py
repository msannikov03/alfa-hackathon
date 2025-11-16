import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class ComplianceAlert(Base):
    __tablename__ = "compliance_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False)
    legal_update_id = Column(UUID(as_uuid=True), ForeignKey("legal_updates.id"), nullable=False)

    status = Column(String, nullable=False, default='pending')  # 'pending', 'completed', 'overdue'
    action_required = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
