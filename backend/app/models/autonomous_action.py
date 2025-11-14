from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base


class AutonomousAction(Base):
    __tablename__ = "autonomous_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    description = Column(String, nullable=True)
    impact_amount = Column(Float, nullable=True)
    required_approval = Column(Boolean, default=False)
    was_approved = Column(Boolean, nullable=True)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    action_metadata = Column(JSON, default={})

    def __repr__(self):
        return f"<AutonomousAction {self.id} - {self.action_type}>"
