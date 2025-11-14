from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Date
from sqlalchemy.sql import func
from app.database import Base


class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    content = Column(JSON, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Briefing {self.id} - {self.date}>"
