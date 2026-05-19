import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ScoreResult(Base):
    __tablename__ = "score_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    overall_score = Column(Integer, nullable=False)
    keyword_score = Column(Integer, nullable=False)
    skills_score = Column(Integer, nullable=False)
    experience_score = Column(Integer, nullable=False)
    format_score = Column(Integer, nullable=False)
    matched_keywords = Column(JSON, nullable=True)
    missing_keywords = Column(JSON, nullable=True)
    matched_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scan = relationship("Scan", back_populates="score_result")
    suggestions = relationship("Suggestion", back_populates="score_result")