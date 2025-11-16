from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.database import Base


class LearnedPattern(Base):
    __tablename__ = "learned_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    pattern_type = Column(String(50), nullable=True)
    trigger_conditions = Column(JSON, nullable=True)
    recommended_action = Column(String, nullable=True)
    success_rate = Column(Float, default=0.5)
    times_used = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<LearnedPattern {self.id} - {self.pattern_type}>"
