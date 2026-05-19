# from pydantic import BaseModel
# from typing import List, Optional


# class SuggestionResponse(BaseModel):
#     category: str
#     priority: str
#     suggestion_text: str

#     class Config:
#         from_attributes = True


# class ScanResultResponse(BaseModel):
#     scan_id: str
#     resume_filename: str

#     overall_score: int
#     keyword_score: int
#     skills_score: int
#     experience_score: int
#     format_score: int

#     matched_keywords: List[str]
#     missing_keywords: List[str]
#     matched_skills: List[str]
#     missing_skills: List[str]

#     suggestions: List[SuggestionResponse]

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime


class SuggestionResponse(BaseModel):
    id: Optional[UUID] = None
    category: str
    priority: str
    suggestion_text: str

    class Config:
        from_attributes = True


class ScanResultResponse(BaseModel):
    scan_id: UUID
    resume_filename: str

    overall_score: int
    keyword_score: int
    skills_score: int
    experience_score: int
    format_score: int

    matched_keywords: List[str]
    missing_keywords: List[str]
    matched_skills: List[str]
    missing_skills: List[str]

    suggestions: List[SuggestionResponse]


class ScanHistoryItem(BaseModel):
    scan_id: UUID
    resume_filename: str
    status: str
    created_at: datetime
    overall_score: Optional[int] = None


class ScanDetailResponse(BaseModel):
    scan_id: UUID
    resume_filename: str
    status: str
    created_at: datetime

    job_description: str

    overall_score: int
    keyword_score: int
    skills_score: int
    experience_score: int
    format_score: int

    matched_keywords: List[str]
    missing_keywords: List[str]
    matched_skills: List[str]
    missing_skills: List[str]

    suggestions: List[SuggestionResponse]