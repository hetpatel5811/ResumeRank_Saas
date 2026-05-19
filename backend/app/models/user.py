import uuid
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    plan = Column(String, default="free")
    scan_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scans = relationship("Scan", back_populates="user")
    job_descriptions = relationship("JobDescription", back_populates="user")