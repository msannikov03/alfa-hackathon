import uuid
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base

class BusinessContext(Base):
    __tablename__ = "business_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    raw_description = Column(String, nullable=False)
    structured_data = Column(JSON, nullable=True) # {industry, business_type, location, keywords}
    
    # The embedding will be stored as a list of floats.
    # For real applications, a dedicated vector type from pgvector would be better.
    embedding = Column(ARRAY(String), nullable=True)