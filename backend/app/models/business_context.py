from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class BusinessContext(Base):
    __tablename__ = "business_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    business_name = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    location = Column(String, nullable=True)
    operating_hours = Column(JSON, nullable=True)
    average_daily_revenue = Column(Integer, nullable=True)
    typical_customer_count = Column(Integer, nullable=True)
    employee_count = Column(Integer, nullable=True)
    key_metrics = Column(JSON, default={})
    decision_thresholds = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<BusinessContext {self.business_name}>"
