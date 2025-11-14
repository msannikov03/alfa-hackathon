from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    decision_type = Column(String(50), nullable=True)
    context = Column(JSON, nullable=True)
    action_taken = Column(String, nullable=True)
    outcome = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    owner_override = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Decision {self.id} - {self.decision_type}>"
