# from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.core.dependencies import get_current_user
# from app.models.user import User
# from app.models.job_description import JobDescription
# from app.models.scan import Scan
# from app.models.score_result import ScoreResult
# from app.models.suggestion import Suggestion
# from app.schemas.scan_schema import ScanResultResponse
# from app.services.file_parser import save_upload_file, extract_resume_text
# from app.services.scoring_engine import run_resume_scoring, extract_top_keywords
# from app.services.suggestion_engine import generate_suggestions


# router = APIRouter(prefix="/api/scans", tags=["Scans"])


# @router.post("/analyze", response_model=ScanResultResponse)
# def analyze_resume(
#     job_description: str = Form(...),
#     resume: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     allowed_extensions = [".pdf", ".docx"]

#     if not any(resume.filename.lower().endswith(ext) for ext in allowed_extensions):
#         raise HTTPException(
#             status_code=400,
#             detail="Only PDF and DOCX files are allowed"
#         )

#     file_path = save_upload_file(resume)
#     resume_text = extract_resume_text(file_path)

#     if not resume_text:
#         raise HTTPException(
#             status_code=400,
#             detail="Could not extract text from resume"
#         )

#     jd_keywords = extract_top_keywords(job_description)

#     jd_record = JobDescription(
#         user_id=current_user.id,
#         raw_text=job_description,
#         extracted_keywords=jd_keywords
#     )

#     db.add(jd_record)
#     db.commit()
#     db.refresh(jd_record)

#     scan = Scan(
#         user_id=current_user.id,
#         job_description_id=jd_record.id,
#         resume_filename=resume.filename,
#         status="completed"
#     )

#     db.add(scan)
#     db.commit()
#     db.refresh(scan)

#     score_data = run_resume_scoring(job_description, resume_text)

#     score_result = ScoreResult(
#         scan_id=scan.id,
#         overall_score=score_data["overall_score"],
#         keyword_score=score_data["keyword_score"],
#         skills_score=score_data["skills_score"],
#         experience_score=score_data["experience_score"],
#         format_score=score_data["format_score"],
#         matched_keywords=score_data["matched_keywords"],
#         missing_keywords=score_data["missing_keywords"],
#         matched_skills=score_data["matched_skills"],
#         missing_skills=score_data["missing_skills"]
#     )

#     db.add(score_result)
#     db.commit()
#     db.refresh(score_result)

#     suggestions_data = generate_suggestions(score_data)

#     suggestion_records = []

#     for item in suggestions_data:
#         suggestion = Suggestion(
#             score_result_id=score_result.id,
#             category=item["category"],
#             priority=item["priority"],
#             suggestion_text=item["suggestion_text"]
#         )

#         db.add(suggestion)
#         suggestion_records.append(suggestion)

#     current_user.scan_count += 1

#     db.commit()

#     return {
#         "scan_id": str(scan.id),
#         "resume_filename": scan.resume_filename,
#         "overall_score": score_result.overall_score,
#         "keyword_score": score_result.keyword_score,
#         "skills_score": score_result.skills_score,
#         "experience_score": score_result.experience_score,
#         "format_score": score_result.format_score,
#         "matched_keywords": score_result.matched_keywords or [],
#         "missing_keywords": score_result.missing_keywords or [],
#         "matched_skills": score_result.matched_skills or [],
#         "missing_skills": score_result.missing_skills or [],
#         "suggestions": suggestions_data
#     }


# @router.get("/history")
# def get_scan_history(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     scans = (
#         db.query(Scan)
#         .filter(Scan.user_id == current_user.id)
#         .order_by(Scan.created_at.desc())
#         .all()
#     )

#     response = []

#     for scan in scans:
#         result = scan.score_result

#         response.append({
#             "scan_id": str(scan.id),
#             "resume_filename": scan.resume_filename,
#             "status": scan.status,
#             "created_at": scan.created_at,
#             "overall_score": result.overall_score if result else None
#         })

#     return response

import os
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.job_description import JobDescription
from app.models.scan import Scan
from app.models.score_result import ScoreResult
from app.models.suggestion import Suggestion
from app.schemas.scan_schema import ScanResultResponse, ScanDetailResponse, ScanHistoryItem
from app.services.file_parser import save_upload_file, extract_resume_text
from app.services.scoring_engine import run_resume_scoring, extract_top_keywords
from app.services.suggestion_engine import generate_suggestions
from app.services.plan_service import get_scan_limit_for_plan


router = APIRouter(prefix="/api/scans", tags=["Scans"])


def build_scan_response(scan: Scan, score_result: ScoreResult, suggestions):
    return {
        "scan_id": scan.id,
        "resume_filename": scan.resume_filename,
        "overall_score": score_result.overall_score,
        "keyword_score": score_result.keyword_score,
        "skills_score": score_result.skills_score,
        "experience_score": score_result.experience_score,
        "format_score": score_result.format_score,
        "matched_keywords": score_result.matched_keywords or [],
        "missing_keywords": score_result.missing_keywords or [],
        "matched_skills": score_result.matched_skills or [],
        "missing_skills": score_result.missing_skills or [],
        "suggestions": suggestions
    }


@router.post("/analyze", response_model=ScanResultResponse)
def analyze_resume(
    job_description: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan_limit = get_scan_limit_for_plan(current_user.plan)

    if scan_limit is not None and current_user.scan_count >= scan_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your current plan scan limit is reached. Upgrade to Plus or Pro to continue."
        )

    allowed_extensions = [".pdf", ".docx"]

    if not any(resume.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed"
        )

    file_path = save_upload_file(resume, str(current_user.id))
    resume_text = extract_resume_text(file_path)

    if not resume_text:
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from resume"
        )

    jd_keywords = extract_top_keywords(job_description)

    jd_record = JobDescription(
        user_id=current_user.id,
        raw_text=job_description,
        extracted_keywords=jd_keywords
    )

    db.add(jd_record)
    db.commit()
    db.refresh(jd_record)

    scan = Scan(
        user_id=current_user.id,
        job_description_id=jd_record.id,
        resume_s3_key=file_path,
        resume_filename=resume.filename,
        status="completed"
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    score_data = run_resume_scoring(job_description, resume_text)

    score_result = ScoreResult(
        scan_id=scan.id,
        overall_score=score_data["overall_score"],
        keyword_score=score_data["keyword_score"],
        skills_score=score_data["skills_score"],
        experience_score=score_data["experience_score"],
        format_score=score_data["format_score"],
        matched_keywords=score_data["matched_keywords"],
        missing_keywords=score_data["missing_keywords"],
        matched_skills=score_data["matched_skills"],
        missing_skills=score_data["missing_skills"]
    )

    db.add(score_result)
    db.commit()
    db.refresh(score_result)

    suggestions_data = generate_suggestions(score_data)

    suggestion_records = []

    for item in suggestions_data:
        suggestion = Suggestion(
            score_result_id=score_result.id,
            category=item["category"],
            priority=item["priority"],
            suggestion_text=item["suggestion_text"]
        )

        db.add(suggestion)
        suggestion_records.append(suggestion)

    current_user.scan_count += 1

    db.commit()

    return build_scan_response(scan, score_result, suggestions_data)


@router.get("/history", response_model=list[ScanHistoryItem])
def get_scan_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )

    response = []

    for scan in scans:
        result = scan.score_result

        response.append({
            "scan_id": scan.id,
            "resume_filename": scan.resume_filename,
            "status": scan.status,
            "created_at": scan.created_at,
            "overall_score": result.overall_score if result else None
        })

    return response


@router.get("/{scan_id}", response_model=ScanDetailResponse)
def get_scan_detail(
    scan_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = (
        db.query(Scan)
        .filter(
            Scan.id == scan_id,
            Scan.user_id == current_user.id
        )
        .first()
    )

    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )

    score_result = scan.score_result

    if not score_result:
        raise HTTPException(
            status_code=404,
            detail="Score result not found"
        )

    suggestions = [
        {
            "id": suggestion.id,
            "category": suggestion.category,
            "priority": suggestion.priority,
            "suggestion_text": suggestion.suggestion_text
        }
        for suggestion in score_result.suggestions
    ]

    return {
        "scan_id": scan.id,
        "resume_filename": scan.resume_filename,
        "status": scan.status,
        "created_at": scan.created_at,
        "job_description": scan.job_description.raw_text,
        "overall_score": score_result.overall_score,
        "keyword_score": score_result.keyword_score,
        "skills_score": score_result.skills_score,
        "experience_score": score_result.experience_score,
        "format_score": score_result.format_score,
        "matched_keywords": score_result.matched_keywords or [],
        "missing_keywords": score_result.missing_keywords or [],
        "matched_skills": score_result.matched_skills or [],
        "missing_skills": score_result.missing_skills or [],
        "suggestions": suggestions
    }


@router.delete("/{scan_id}")
def delete_scan(
    scan_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = (
        db.query(Scan)
        .filter(
            Scan.id == scan_id,
            Scan.user_id == current_user.id
        )
        .first()
    )

    if not scan:
        raise HTTPException(
            status_code=404,
            detail="Scan not found"
        )

    # Delete local uploaded file if exists
    if scan.resume_s3_key and os.path.exists(scan.resume_s3_key):
        os.remove(scan.resume_s3_key)

    score_result = scan.score_result

    if score_result:
        db.query(Suggestion).filter(
            Suggestion.score_result_id == score_result.id
        ).delete()

        db.delete(score_result)

    job_description = scan.job_description

    db.delete(scan)

    if job_description:
        db.delete(job_description)

    if current_user.scan_count > 0:
        current_user.scan_count -= 1

    db.commit()

    return {
        "message": "Scan deleted successfully"
    }
