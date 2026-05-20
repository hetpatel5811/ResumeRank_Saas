from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.job_application import JobApplication
from app.models.user import User
from app.schemas.career_schema import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
    JobTrackerSummary,
)


router = APIRouter(prefix="/api/jobs", tags=["Job Tracker"])


@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_job_application(
    payload: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = JobApplication(
        user_id=current_user.id,
        company=payload.company.strip(),
        role=payload.role.strip(),
        status=payload.status,
        job_url=payload.job_url,
        location=payload.location,
        salary_text=payload.salary_text,
        notes=payload.notes,
        follow_up_at=payload.follow_up_at,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get("", response_model=list[JobApplicationResponse])
def list_job_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(JobApplication)
        .filter(JobApplication.user_id == current_user.id)
        .order_by(JobApplication.updated_at.desc())
        .all()
    )

    return rows


@router.get("/summary", response_model=JobTrackerSummary)
def get_job_tracker_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now_utc = datetime.now(timezone.utc)
    next_week = now_utc + timedelta(days=7)
    open_statuses = ("saved", "applied", "screening", "interview")

    rows = (
        db.query(JobApplication.status)
        .filter(JobApplication.user_id == current_user.id)
        .all()
    )

    counts: dict[str, int] = {}
    for (status_value,) in rows:
        counts[status_value] = counts.get(status_value, 0) + 1

    overdue_follow_ups = (
        db.query(JobApplication.id)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.follow_up_at.isnot(None),
            JobApplication.follow_up_at < now_utc,
            JobApplication.status.in_(open_statuses),
        )
        .count()
    )

    due_next_7_days = (
        db.query(JobApplication.id)
        .filter(
            JobApplication.user_id == current_user.id,
            JobApplication.follow_up_at.isnot(None),
            JobApplication.follow_up_at >= now_utc,
            JobApplication.follow_up_at <= next_week,
            JobApplication.status.in_(open_statuses),
        )
        .count()
    )

    return {
        "total": len(rows),
        "by_status": counts,
        "overdue_follow_ups": overdue_follow_ups,
        "due_next_7_days": due_next_7_days,
    }


@router.get("/{job_id}", response_model=JobApplicationResponse)
def get_job_application(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(JobApplication)
        .filter(JobApplication.id == job_id, JobApplication.user_id == current_user.id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Job application not found")

    return row


@router.patch("/{job_id}", response_model=JobApplicationResponse)
def update_job_application(
    job_id: UUID,
    payload: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(JobApplication)
        .filter(JobApplication.id == job_id, JobApplication.user_id == current_user.id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Job application not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(row, key, value)

    db.commit()
    db.refresh(row)
    return row


@router.delete("/{job_id}")
def delete_job_application(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(JobApplication)
        .filter(JobApplication.id == job_id, JobApplication.user_id == current_user.id)
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Job application not found")

    db.delete(row)
    db.commit()

    return {"message": "Job application deleted successfully"}
