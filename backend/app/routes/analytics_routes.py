from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.job_application import JobApplication
from app.models.scan import Scan
from app.models.user import User


router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    total_scans = (
        db.query(func.count(Scan.id))
        .filter(Scan.user_id == current_user.id)
        .scalar()
    ) or 0

    scans_last_30_days = (
        db.query(func.count(Scan.id))
        .filter(Scan.user_id == current_user.id, Scan.created_at >= thirty_days_ago)
        .scalar()
    ) or 0

    total_jobs_tracked = (
        db.query(func.count(JobApplication.id))
        .filter(JobApplication.user_id == current_user.id)
        .scalar()
    ) or 0

    pipeline = (
        db.query(JobApplication.status, func.count(JobApplication.id))
        .filter(JobApplication.user_id == current_user.id)
        .group_by(JobApplication.status)
        .all()
    )

    pipeline_breakdown = {status_value: count for status_value, count in pipeline}

    return {
        "total_scans": total_scans,
        "scans_last_30_days": scans_last_30_days,
        "total_jobs_tracked": total_jobs_tracked,
        "pipeline_breakdown": pipeline_breakdown,
    }
