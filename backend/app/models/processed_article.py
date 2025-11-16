from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class ProcessedArticle(Base):
    __tablename__ = "processed_articles"

    url = Column(String, primary_key=True)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
