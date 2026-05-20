from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


JobStatus = Literal[
    "saved",
    "applied",
    "screening",
    "interview",
    "offer",
    "rejected",
]


class JobApplicationCreate(BaseModel):
    company: str
    role: str
    status: JobStatus = "saved"
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary_text: Optional[str] = None
    notes: Optional[str] = None
    follow_up_at: Optional[datetime] = None


class JobApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[JobStatus] = None
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary_text: Optional[str] = None
    notes: Optional[str] = None
    follow_up_at: Optional[datetime] = None


class JobApplicationResponse(BaseModel):
    id: UUID
    company: str
    role: str
    status: JobStatus
    job_url: Optional[str] = None
    location: Optional[str] = None
    salary_text: Optional[str] = None
    notes: Optional[str] = None
    follow_up_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobTrackerSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    overdue_follow_ups: int
    due_next_7_days: int


class CoverLetterRequest(BaseModel):
    target_role: str
    company_name: str
    job_description: str
    resume_points: list[str] = Field(default_factory=list)
    tone: Literal["professional", "confident", "concise"] = "professional"


class CoverLetterResponse(BaseModel):
    cover_letter: str
    checklist: list[str]


class LinkedInOptimizeRequest(BaseModel):
    linkedin_text: str
    job_description: str


class LinkedInOptimizeResponse(BaseModel):
    optimized_headline: str
    about_suggestions: list[str]
    missing_keywords: list[str]


class InterviewPracticeRequest(BaseModel):
    target_role: str
    job_description: str
    experience_level: Literal["fresher", "mid", "senior"] = "mid"


class InterviewQuestionItem(BaseModel):
    category: str
    question: str
    why_it_matters: str


class InterviewPracticeResponse(BaseModel):
    questions: list[InterviewQuestionItem]


class BulletOptimizeRequest(BaseModel):
    bullet_points: list[str]
    job_description: str


class BulletOptimizeItem(BaseModel):
    original: str
    optimized: str
    reasoning: str


class BulletOptimizeResponse(BaseModel):
    optimized_bullets: list[BulletOptimizeItem]
    keywords_used: list[str]


class OutreachEmailRequest(BaseModel):
    target_role: str
    company_name: str
    context_notes: str
    highlights: list[str] = Field(default_factory=list)
    tone: Literal["professional", "warm", "concise"] = "professional"


class OutreachEmailResponse(BaseModel):
    subject: str
    body: str
    checklist: list[str]
