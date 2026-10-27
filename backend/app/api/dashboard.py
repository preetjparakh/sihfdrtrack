from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.clock import clock_service
from backend.app.api.deps import get_current_user
from backend.app.models.models import User, Submission, Discrepancy, ReleaseRequest, Renewal
from backend.app.schemas.schemas import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardStatsResponse)
def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub_query = db.query(Submission)
    disc_query = db.query(Discrepancy)
    rel_query = db.query(ReleaseRequest)
    renewal_query = db.query(Renewal)

    if current_user.role == "COLLEGE":
        sub_query = sub_query.filter(Submission.institution_id == current_user.institution_id)
        disc_query = disc_query.join(Submission).filter(Submission.institution_id == current_user.institution_id)
        rel_query = rel_query.join(Submission).filter(Submission.institution_id == current_user.institution_id)
        renewal_query = renewal_query.join(
            Submission, Renewal.predecessor_submission_id == Submission.id
        ).filter(Submission.institution_id == current_user.institution_id)

    submissions = sub_query.all()
    today = clock_service.today_local_date()

    total = len(submissions)
    pending_review = sum(1 for s in submissions if s.review_status in ("SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"))
    under_review = sum(1 for s in submissions if s.review_status == "UNDER_REVIEW")
    pending_bank = sum(1 for s in submissions if s.verification_status in ("NOT_INITIATED", "PENDING", "SOURCE_UNAVAILABLE", "MANUAL_REQUIRED"))
    confirmed = sum(1 for s in submissions if s.verification_status == "CONFIRMED")
    mismatched = sum(1 for s in submissions if s.verification_status == "MISMATCH")
    completed_release_ids = {
        row[0] for row in rel_query.filter(ReleaseRequest.status == "COMPLETED")
        .with_entities(ReleaseRequest.submission_id).all()
    }

    # Maturity categorization based on local calendar dates
    approaching_maturity = 0
    matured = 0
    for s in submissions:
        if (s.review_status != "ACCEPTED"
                or s.entered_instrument_status in ("RELEASED", "SUPERSEDED")
                or s.id in completed_release_ids):
            continue
        if s.entered_maturity_date:
            try:
                mat_date = date.fromisoformat(s.entered_maturity_date)
                delta_days = (mat_date - today).days
                if delta_days <= 0:
                    matured += 1
                elif 0 < delta_days <= 90:
                    approaching_maturity += 1
            except ValueError:
                pass

    active_discrepancies = disc_query.filter(Discrepancy.resolution.is_(None)).count()
    pending_renewals = renewal_query.filter(Renewal.status == "PENDING").count()
    pending_releases = rel_query.filter(ReleaseRequest.status.in_(["REQUESTED", "UNDER_REVIEW", "RECOMMENDED", "APPROVED_EXECUTION_PENDING"])).count()

    return DashboardStatsResponse(
        demo_clock=clock_service.now_iso(),
        display_time=clock_service.now_display(),
        total_submissions=total,
        pending_review=pending_review,
        under_review=under_review,
        pending_bank_confirmation=pending_bank,
        confirmed_submissions=confirmed,
        mismatched_submissions=mismatched,
        active_discrepancies=active_discrepancies,
        approaching_maturity=approaching_maturity,
        matured=matured,
        pending_renewals=pending_renewals,
        pending_releases=pending_releases
    )
