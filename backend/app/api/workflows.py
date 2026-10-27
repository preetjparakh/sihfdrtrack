import csv
import hashlib
import io
import json
import uuid
from datetime import datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.api.deps import (
    get_current_user,
    require_approver_user,
    require_college_user,
    require_officer_user,
    verify_institution_access,
)
from backend.app.core.clock import clock_service
from backend.app.core.database import get_db
from backend.app.models.models import (
    AuditLog,
    BankVerification,
    Discrepancy,
    Document,
    ManualConfirmation,
    Notification,
    OCRResult,
    ReleaseRequest,
    Renewal,
    Submission,
    User,
)
from backend.app.services.audit import log_audit_event

router = APIRouter(tags=["workflows"])

REMINDER_OFFSETS = (90, 60, 30, 7, 1, 0, -1, -7)


class RenewalRequest(BaseModel):
    application_reference: str
    instrument_type: str = "FDR"
    bank_id: str
    fdr_number: str
    depositor_name: str
    principal_amount: str
    currency: str = "INR"
    issue_date: str
    maturity_date: str
    beneficiary_name: Optional[str] = "AICTE (demo only)"
    lien_status: Optional[str] = "MARKED"
    lien_in_favour_of: Optional[str] = "AICTE (demo only)"


class ReleaseRequestPayload(BaseModel):
    request_type: str = "RELEASE"
    reason: str = Field(min_length=5, max_length=2000)


class RecommendationPayload(BaseModel):
    recommendation: str = Field(min_length=5, max_length=2000)
    zero_liabilities_verified: bool


class AuthorityDecisionPayload(BaseModel):
    decision: str
    reason: str = Field(min_length=5, max_length=2000)


class ExecutionPayload(BaseModel):
    discharge_reference: str = Field(min_length=3, max_length=100)
    evidence: str = Field(min_length=5, max_length=2000)


def _submission_or_404(db: Session, submission_id: str) -> Submission:
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    return submission


def _is_active_instrument(db: Session, submission: Submission) -> bool:
    if submission.entered_instrument_status != "ACTIVE":
        return False
    completed_release = db.query(ReleaseRequest.id).filter(
        ReleaseRequest.submission_id == submission.id,
        ReleaseRequest.status == "COMPLETED",
    ).first()
    return completed_release is None


def _local_midnight_utc(day, timezone_name: str) -> str:
    local_dt = datetime.combine(day, time.min, tzinfo=ZoneInfo(timezone_name))
    return local_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _csv_safe(value) -> str:
    text = "" if value is None else str(value)
    if text.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


@router.post("/api/submissions/{submission_id}/renewal")
def create_successor_submission(
    submission_id: str,
    payload: RenewalRequest,
    current_user: User = Depends(require_college_user),
    db: Session = Depends(get_db),
):
    predecessor = _submission_or_404(db, submission_id)
    verify_institution_access(predecessor.institution_id, current_user)
    if predecessor.review_status != "ACCEPTED":
        raise HTTPException(status_code=409, detail="Only an accepted predecessor can be renewed.")
    if not _is_active_instrument(db, predecessor):
        raise HTTPException(status_code=409, detail="Only an active instrument can be renewed.")
    if db.query(Renewal).filter(
        Renewal.predecessor_submission_id == predecessor.id,
        Renewal.status == "PENDING",
    ).first():
        raise HTTPException(status_code=409, detail="A successor is already awaiting acceptance.")

    now = clock_service.now_iso()
    successor = Submission(
        id=f"SUB-{uuid.uuid4().hex[:8].upper()}",
        institution_id=predecessor.institution_id,
        scenario="CUSTOM_RENEWAL",
        application_reference=payload.application_reference,
        instrument_type=payload.instrument_type,
        entered_bank_id=payload.bank_id,
        entered_fdr_number=payload.fdr_number.strip(),
        entered_depositor_name=payload.depositor_name.strip(),
        entered_principal_amount=payload.principal_amount.strip(),
        entered_currency=payload.currency,
        entered_issue_date=payload.issue_date,
        entered_maturity_date=payload.maturity_date,
        entered_instrument_status="ACTIVE",
        entered_beneficiary_name=payload.beneficiary_name,
        entered_lien_status=payload.lien_status,
        entered_lien_in_favour_of=payload.lien_in_favour_of,
        entered_status_as_of=now,
        entered_record_updated_at=now,
        review_status="DRAFT",
        verification_status="NOT_INITIATED",
        submitted_at=now,
        assigned_officer_id="USER-O01",
        predecessor_submission_id=predecessor.id,
    )
    renewal = Renewal(
        id=f"REN-{uuid.uuid4().hex[:10].upper()}",
        predecessor_submission_id=predecessor.id,
        successor_submission_id=successor.id,
        linked_at=now,
        status="PENDING",
    )
    db.add(successor)
    db.flush()
    db.add(renewal)
    db.commit()
    log_audit_event(
        db, "renewal", renewal.id, current_user.id, "SUCCESSOR_DRAFT_LINKED",
        after_state={"predecessor": predecessor.id, "successor": successor.id, "status": "PENDING"},
    )
    return {"renewal_id": renewal.id, "predecessor": predecessor.id, "successor": successor.id, "status": renewal.status}


@router.get("/api/renewals")
def list_renewals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Renewal).order_by(Renewal.linked_at.desc())
    if current_user.role == "COLLEGE":
        query = query.join(
            Submission, Renewal.predecessor_submission_id == Submission.id
        ).filter(Submission.institution_id == current_user.institution_id)
    return [
        {
            "id": renewal.id,
            "predecessor": _submission_summary(db, renewal.predecessor_submission_id),
            "successor": _submission_summary(db, renewal.successor_submission_id),
            "status": renewal.status,
            "linked_at": renewal.linked_at,
        }
        for renewal in query.all()
    ]


def _submission_summary(db: Session, submission_id: str):
    item = db.query(Submission).filter(Submission.id == submission_id).first()
    if not item:
        return None
    return {
        "id": item.id,
        "institution_id": item.institution_id,
        "application_reference": item.application_reference,
        "fdr_number": item.entered_fdr_number,
        "amount": item.entered_principal_amount,
        "maturity_date": item.entered_maturity_date,
        "review_status": item.review_status,
        "verification_status": item.verification_status,
    }


@router.post("/api/submissions/{submission_id}/release-requests")
def request_release(
    submission_id: str,
    payload: ReleaseRequestPayload,
    current_user: User = Depends(require_college_user),
    db: Session = Depends(get_db),
):
    submission = _submission_or_404(db, submission_id)
    verify_institution_access(submission.institution_id, current_user)
    if submission.review_status != "ACCEPTED":
        raise HTTPException(status_code=409, detail="Only an accepted instrument can be released.")
    if not _is_active_instrument(db, submission):
        raise HTTPException(status_code=409, detail="Only an active instrument can be released.")
    if payload.request_type not in {"RELEASE", "REFUND", "DISCHARGE"}:
        raise HTTPException(status_code=422, detail="Unsupported release request type.")
    active = db.query(ReleaseRequest).filter(
        ReleaseRequest.submission_id == submission.id,
        ReleaseRequest.status.in_(["REQUESTED", "UNDER_REVIEW", "RECOMMENDED", "APPROVED_EXECUTION_PENDING"]),
    ).first()
    if active:
        raise HTTPException(status_code=409, detail="An active release request already exists.")
    release = ReleaseRequest(
        id=f"REL-{uuid.uuid4().hex[:10].upper()}",
        submission_id=submission.id,
        request_type=payload.request_type,
        reason=payload.reason,
        status="REQUESTED",
        requested_at=clock_service.now_iso(),
    )
    db.add(release)
    db.commit()
    log_audit_event(db, "release_request", release.id, current_user.id, "RELEASE_REQUESTED",
                    after_state={"status": release.status, "reason": release.reason})
    return _release_payload(release)


def _release_payload(release: ReleaseRequest):
    return {
        "id": release.id,
        "submission_id": release.submission_id,
        "request_type": release.request_type,
        "reason": release.reason,
        "status": release.status,
        "requested_at": release.requested_at,
        "officer_recommendation": release.officer_recommendation,
        "recommended_at": release.recommended_at,
        "authority_decision": release.authority_decision,
        "decision_reason": release.decision_reason,
        "approved_at": release.approved_at,
        "execution_reference": release.execution_reference,
        "executed_at": release.executed_at,
    }


@router.get("/api/release-requests")
def list_release_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ReleaseRequest).join(Submission).order_by(ReleaseRequest.requested_at.desc())
    if current_user.role == "COLLEGE":
        query = query.filter(Submission.institution_id == current_user.institution_id)
    return [_release_payload(item) for item in query.all()]


@router.post("/api/release-requests/{release_id}/recommend")
def recommend_release(
    release_id: str,
    payload: RecommendationPayload,
    current_user: User = Depends(require_officer_user),
    db: Session = Depends(get_db),
):
    release = db.query(ReleaseRequest).filter(ReleaseRequest.id == release_id).first()
    if not release:
        raise HTTPException(status_code=404, detail="Release request not found.")
    if release.status != "REQUESTED":
        raise HTTPException(status_code=409, detail="Only requested releases can be reviewed.")
    release.status = "RECOMMENDED" if payload.zero_liabilities_verified else "RETURNED"
    release.officer_recommendation = payload.recommendation
    release.recommended_at = clock_service.now_iso()
    release.recommended_by = current_user.id
    db.commit()
    log_audit_event(db, "release_request", release.id, current_user.id, "RELEASE_RECOMMENDATION_RECORDED",
                    after_state={
                        "status": release.status,
                        "recommendation": payload.recommendation,
                        "zero_liabilities_verified": payload.zero_liabilities_verified,
                    })
    return _release_payload(release)


@router.post("/api/release-requests/{release_id}/decision")
def decide_release(
    release_id: str,
    payload: AuthorityDecisionPayload,
    current_user: User = Depends(require_approver_user),
    db: Session = Depends(get_db),
):
    release = db.query(ReleaseRequest).filter(ReleaseRequest.id == release_id).first()
    if not release:
        raise HTTPException(status_code=404, detail="Release request not found.")
    if release.status != "RECOMMENDED":
        raise HTTPException(status_code=409, detail="Authority decision requires an officer recommendation.")
    decision = payload.decision.upper()
    if decision not in {"APPROVED", "REJECTED", "RETURNED"}:
        raise HTTPException(status_code=422, detail="Decision must be APPROVED, REJECTED, or RETURNED.")
    before = release.status
    release.authority_decision = decision
    release.decision_reason = payload.reason
    release.approved_by = current_user.id
    release.approved_at = clock_service.now_iso()
    release.status = {
        "APPROVED": "APPROVED_EXECUTION_PENDING",
        "REJECTED": "REJECTED",
        "RETURNED": "RETURNED",
    }[decision]
    db.commit()
    log_audit_event(db, "release_request", release.id, current_user.id, "RELEASE_AUTHORITY_DECISION",
                    before_state={"status": before},
                    after_state={"status": release.status, "decision": decision, "reason": payload.reason})
    return _release_payload(release)


@router.post("/api/release-requests/{release_id}/execute")
def execute_release(
    release_id: str,
    payload: ExecutionPayload,
    current_user: User = Depends(require_officer_user),
    db: Session = Depends(get_db),
):
    release = db.query(ReleaseRequest).filter(ReleaseRequest.id == release_id).first()
    if not release:
        raise HTTPException(status_code=404, detail="Release request not found.")
    if release.status != "APPROVED_EXECUTION_PENDING":
        raise HTTPException(status_code=409, detail="Execution is permitted only after authority approval.")
    submission = _submission_or_404(db, release.submission_id)
    previous_instrument_status = submission.entered_instrument_status
    release.execution_reference = payload.discharge_reference.strip()
    release.execution_evidence = payload.evidence
    release.executed_by = current_user.id
    release.executed_at = clock_service.now_iso()
    release.status = "COMPLETED"
    submission.entered_instrument_status = "RELEASED"
    db.commit()
    log_audit_event(db, "release_request", release.id, current_user.id, "RELEASE_EXECUTION_CONFIRMED",
                    before_state={"status": "APPROVED_EXECUTION_PENDING", "instrument_status": previous_instrument_status},
                    after_state={"status": release.status, "instrument_status": submission.entered_instrument_status,
                                 "discharge_reference": release.execution_reference})
    return _release_payload(release)


@router.post("/api/reminders/run")
def run_reminder_job(
    current_user: User = Depends(require_officer_user),
    db: Session = Depends(get_db),
):
    today = clock_service.today_local_date()
    tz_name = clock_service._tz.key
    created = 0
    sent = 0
    rescheduled = 0

    candidates = db.query(Submission).filter(
        Submission.review_status == "ACCEPTED",
        Submission.entered_instrument_status == "ACTIVE",
    ).all()
    candidates = [item for item in candidates if _is_active_instrument(db, item)]
    for submission in candidates:
        deadlines = (
            ("MATURITY", submission.entered_maturity_date),
            ("RENEWAL", submission.renewal_due_date),
        )
        for deadline_type, deadline_text in deadlines:
            if not deadline_text:
                continue
            try:
                deadline = datetime.strptime(deadline_text[:10], "%Y-%m-%d").date()
            except ValueError:
                continue
            for offset in REMINDER_OFFSETS:
                notification_day = deadline - timedelta(days=offset)
                recipient_id = (
                    submission.assigned_officer_id or "USER-O01"
                    if offset < 0
                    else db.query(User.id).filter(
                        User.institution_id == submission.institution_id,
                        User.role == "COLLEGE",
                    ).scalar()
                )
                if not recipient_id:
                    continue
                dedupe_key = (
                    f"{submission.id}:{deadline_type}:{deadline.isoformat()}:{offset}:"
                    f"{recipient_id}:IN_APP"
                )
                existing = db.query(Notification).filter(Notification.dedupe_key == dedupe_key).first()
                if existing:
                    if existing.delivery_status == "SCHEDULED" and notification_day <= today:
                        existing.delivery_status = "SENT"
                        existing.sent_at = clock_service.now_iso()
                        sent += 1
                    continue

                stale = db.query(Notification).filter(
                    Notification.submission_id == submission.id,
                    Notification.deadline_type == deadline_type,
                    Notification.offset_days == offset,
                    Notification.delivery_status == "SCHEDULED",
                ).all()
                for previous in stale:
                    previous.delivery_status = "CANCELLED"
                    rescheduled += 1

                notification = Notification(
                    id=f"NOT-{uuid.uuid4().hex[:10].upper()}",
                    submission_id=submission.id,
                    event_type="MATURITY_REMINDER" if offset >= 0 else "OVERDUE_ESCALATION",
                    deadline_type=deadline_type,
                    due_date=deadline.isoformat(),
                    offset_days=offset,
                    recipient_user_id=recipient_id,
                    channel="IN_APP",
                    scheduled_at=_local_midnight_utc(notification_day, tz_name),
                    delivery_status="SENT" if notification_day <= today else "SCHEDULED",
                    sent_at=clock_service.now_iso() if notification_day <= today else None,
                    dedupe_key=dedupe_key,
                )
                db.add(notification)
                created += 1
                if notification.delivery_status == "SENT":
                    sent += 1

    pending_submissions = db.query(Submission).filter(
        Submission.review_status.in_(("SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"))
    ).all()
    college_recipients = {
        row.institution_id: row.id
        for row in db.query(User).filter(User.role == "COLLEGE").all()
    }
    action_alerts = []
    for submission in pending_submissions:
        action_alerts.append((
            submission,
            "PENDING_REVIEW_ALERT",
            "PENDING_REVIEW",
            submission.assigned_officer_id or "USER-O01",
            submission.id,
        ))
        open_discrepancies = db.query(Discrepancy).filter(
            Discrepancy.submission_id == submission.id,
            Discrepancy.resolution.is_(None),
        ).all()
        for discrepancy in open_discrepancies:
            recipient = (
                college_recipients.get(submission.institution_id)
                if discrepancy.assigned_to == "COLLEGE"
                else (submission.assigned_officer_id or "USER-O01")
            )
            if recipient:
                action_alerts.append((
                    submission,
                    "OPEN_DISCREPANCY_ALERT",
                    "OPEN_DISCREPANCY",
                    recipient,
                    discrepancy.id,
                ))
    for submission, event_type, deadline_type, recipient_id, source_id in action_alerts:
        dedupe_key = f"{source_id}:{event_type}:{today.isoformat()}:{recipient_id}:IN_APP"
        if db.query(Notification.id).filter(Notification.dedupe_key == dedupe_key).first():
            continue
        db.add(Notification(
            id=f"NOT-{uuid.uuid4().hex[:10].upper()}",
            submission_id=submission.id,
            event_type=event_type,
            deadline_type=deadline_type,
            due_date=today.isoformat(),
            offset_days=0,
            recipient_user_id=recipient_id,
            channel="IN_APP",
            scheduled_at=_local_midnight_utc(today, tz_name),
            sent_at=clock_service.now_iso(),
            delivery_status="SENT",
            dedupe_key=dedupe_key,
        ))
        created += 1
        sent += 1
    db.commit()
    log_audit_event(
        db, "reminder_job", f"REM-{today.isoformat()}", current_user.id, "REMINDER_JOB_RUN",
        after_state={"created": created, "sent": sent, "rescheduled": rescheduled},
    )
    return {"date": today.isoformat(), "created": created, "sent": sent, "rescheduled": rescheduled}


@router.get("/api/notifications")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Notification).filter(
        Notification.recipient_user_id == current_user.id
    ).order_by(Notification.scheduled_at.desc())
    return [
        {
            "id": item.id,
            "submission_id": item.submission_id,
            "event_type": item.event_type,
            "deadline_type": item.deadline_type,
            "due_date": item.due_date,
            "offset_days": item.offset_days,
            "scheduled_at": item.scheduled_at,
            "sent_at": item.sent_at,
            "delivery_status": item.delivery_status,
        }
        for item in query.all()
    ]


@router.get("/api/reports")
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Submission)
    if current_user.role == "COLLEGE":
        query = query.filter(Submission.institution_id == current_user.institution_id)
    submissions = query.order_by(Submission.institution_id, Submission.id).all()
    today = clock_service.today_local_date()
    rows = []
    for item in submissions:
        try:
            days_to_maturity = (
                datetime.strptime(item.entered_maturity_date[:10], "%Y-%m-%d").date() - today
            ).days
        except ValueError:
            days_to_maturity = None
        renewal = db.query(Renewal).filter(
            (Renewal.predecessor_submission_id == item.id)
            | (Renewal.successor_submission_id == item.id)
        ).order_by(Renewal.linked_at.desc()).first()
        release = db.query(ReleaseRequest).filter(
            ReleaseRequest.submission_id == item.id
        ).order_by(ReleaseRequest.requested_at.desc()).first()
        instrument_status = item.entered_instrument_status
        if release and release.status == "COMPLETED":
            instrument_status = "RELEASED"
        rows.append({
            "submission_id": item.id,
            "institution_id": item.institution_id,
            "application_reference": item.application_reference,
            "scenario": item.scenario,
            "fdr_number": item.entered_fdr_number,
            "amount": item.entered_principal_amount,
            "review_status": item.review_status,
            "verification_status": item.verification_status,
            "instrument_status": instrument_status,
            "maturity_date": item.entered_maturity_date,
            "days_to_maturity": days_to_maturity,
            "renewal_id": renewal.id if renewal else None,
            "renewal_status": renewal.status if renewal else None,
            "release_status": release.status if release else None,
            "active_discrepancies": db.query(Discrepancy).filter(
                Discrepancy.submission_id == item.id,
                Discrepancy.resolution.is_(None),
            ).count(),
        })
    return {"as_of": clock_service.now_iso(), "items": rows}


@router.get("/api/reports/export.csv")
def export_reports_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = get_reports(current_user, db)
    output = io.StringIO(newline="")
    columns = [
        "submission_id", "institution_id", "application_reference", "scenario",
        "fdr_number", "amount", "review_status", "verification_status", "instrument_status",
        "maturity_date", "days_to_maturity", "renewal_id", "renewal_status", "release_status",
        "active_discrepancies",
    ]
    writer = csv.DictWriter(output, fieldnames=columns, lineterminator="\r\n")
    writer.writeheader()
    for item in report["items"]:
        writer.writerow({key: _csv_safe(item.get(key)) for key in columns})
    content = output.getvalue()
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="aicte-fdr-report.csv"'},
    )


@router.get("/api/audit")
def list_audit_events(
    entity_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    submissions_query = db.query(Submission.id)
    if current_user.role == "COLLEGE":
        submissions_query = submissions_query.filter(Submission.institution_id == current_user.institution_id)
    submission_ids = [row[0] for row in submissions_query.all()]
    related_ids = set(submission_ids)
    if submission_ids:
        related_ids.update(row[0] for row in db.query(Document.id).filter(Document.submission_id.in_(submission_ids)).all())
        related_ids.update(row[0] for row in db.query(OCRResult.id).join(Document).filter(Document.submission_id.in_(submission_ids)).all())
        related_ids.update(row[0] for row in db.query(Discrepancy.id).filter(Discrepancy.submission_id.in_(submission_ids)).all())
        related_ids.update(row[0] for row in db.query(BankVerification.id).filter(BankVerification.submission_id.in_(submission_ids)).all())
        related_ids.update(row[0] for row in db.query(ManualConfirmation.id).filter(ManualConfirmation.submission_id.in_(submission_ids)).all())
        related_ids.update(row[0] for row in db.query(ReleaseRequest.id).filter(ReleaseRequest.submission_id.in_(submission_ids)).all())
        related_ids.update(row[0] for row in db.query(Renewal.id).filter(
            (Renewal.predecessor_submission_id.in_(submission_ids))
            | (Renewal.successor_submission_id.in_(submission_ids))
        ).all())
    query = db.query(AuditLog).filter(AuditLog.entity_id.in_(related_ids))
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action == action)
    logs = query.order_by(AuditLog.timestamp.desc(), AuditLog.id.desc()).limit(limit).all()
    return [
        {
            "id": event.id,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "actor_id": event.actor_id,
            "action": event.action,
            "timestamp": event.timestamp,
            "before_state": json.loads(event.before_state_json) if event.before_state_json else None,
            "after_state": json.loads(event.after_state_json) if event.after_state_json else None,
            "reason": event.reason,
            "source_reference": event.source_reference,
        }
        for event in logs
    ]


@router.get("/api/demo/clock/now")
def clock_now(current_user: User = Depends(get_current_user)):
    return {
        "frozen_iso": clock_service.now_iso(),
        "display_ist": clock_service.now_display(),
        "today_local": clock_service.today_local_date().isoformat(),
        "is_frozen": clock_service._is_frozen,
    }
