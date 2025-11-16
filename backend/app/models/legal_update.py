import uuid
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class LegalUpdate(Base):
    __tablename__ = "legal_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)
    
    summary = Column(Text, nullable=False)
    impact_level = Column(String, nullable=False) # 'High', 'Medium', 'Low'
    category = Column(String, nullable=False)
    
    full_text_hash = Column(String, nullable=False) # To detect if content changed
    
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # The structured data from the LLM
    details = Column(JSON, nullable=True)
