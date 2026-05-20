from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.career_schema import (
    BulletOptimizeRequest,
    BulletOptimizeResponse,
    CoverLetterRequest,
    CoverLetterResponse,
    InterviewPracticeRequest,
    InterviewPracticeResponse,
    LinkedInOptimizeRequest,
    LinkedInOptimizeResponse,
)
from app.services.career_tools_service import (
    generate_cover_letter,
    generate_interview_questions,
    optimize_linkedin_profile,
    optimize_resume_bullets,
)


router = APIRouter(prefix="/api/tools", tags=["Career Tools"])


@router.post("/cover-letter", response_model=CoverLetterResponse)
def create_cover_letter(
    payload: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = generate_cover_letter(
        target_role=payload.target_role,
        company_name=payload.company_name,
        job_description=payload.job_description,
        resume_points=payload.resume_points,
        tone=payload.tone,
    )
    return result


@router.post("/linkedin-optimize", response_model=LinkedInOptimizeResponse)
def linkedin_optimize(
    payload: LinkedInOptimizeRequest,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = optimize_linkedin_profile(
        linkedin_text=payload.linkedin_text,
        job_description=payload.job_description,
    )
    return result


@router.post("/interview-practice", response_model=InterviewPracticeResponse)
def interview_practice(
    payload: InterviewPracticeRequest,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = generate_interview_questions(
        target_role=payload.target_role,
        job_description=payload.job_description,
        experience_level=payload.experience_level,
    )
    return result


@router.post("/optimize-bullets", response_model=BulletOptimizeResponse)
def optimize_bullets(
    payload: BulletOptimizeRequest,
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    result = optimize_resume_bullets(
        bullet_points=payload.bullet_points,
        job_description=payload.job_description,
    )
    return result
