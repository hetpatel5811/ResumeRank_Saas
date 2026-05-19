import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    score_result_id = Column(UUID(as_uuid=True), ForeignKey("score_results.id"), nullable=False)
    category = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    suggestion_text = Column(Text, nullable=False)
    score_result = relationship("ScoreResult", back_populates="suggestions")