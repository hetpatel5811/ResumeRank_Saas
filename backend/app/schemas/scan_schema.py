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


class ATSAuditCheckResponse(BaseModel):
    check_id: str
    title: str
    status: str
    severity: str
    message: str


class ATSAuditResponse(BaseModel):
    score: int
    checks: List[ATSAuditCheckResponse]
    high_impact_fixes: List[str]


class WeightedCategoryResponse(BaseModel):
    category: str
    score: int
    weight: float
    contribution: float


class ImprovementAreaResponse(BaseModel):
    category: str
    score: int
    potential_lift: float


class ScoreDiagnosticsResponse(BaseModel):
    weighted_breakdown: List[WeightedCategoryResponse]
    top_improvement_areas: List[ImprovementAreaResponse]
    high_impact_keywords: List[str]
    high_impact_skills: List[str]


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
    ats_audit: ATSAuditResponse
    score_diagnostics: ScoreDiagnosticsResponse


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
    ats_audit: ATSAuditResponse
    score_diagnostics: ScoreDiagnosticsResponse
