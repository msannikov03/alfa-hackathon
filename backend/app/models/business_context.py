from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class BusinessContext(Base):
    __tablename__ = "business_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    operating_hours = Column(JSON, nullable=True)
    average_daily_revenue = Column(Integer, nullable=True)
    typical_customer_count = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)
    key_metrics = Column(JSON, nullable=True)
    decision_thresholds = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
