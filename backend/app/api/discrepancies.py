from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.clock import clock_service
from backend.app.api.deps import get_current_user, require_officer_user, verify_institution_access
from backend.app.models.models import User, Submission, Discrepancy
from backend.app.schemas.schemas import DiscrepancyResponse
from backend.app.services.audit import log_audit_event

router = APIRouter(tags=["discrepancies"])

class CollegeResponsePayload(BaseModel):
    response: str

class ResolveDiscrepancyPayload(BaseModel):
    resolution: str  # RESOLVED_ACCEPTED, RESOLVED_REJECTED

class IssueDiscrepancyPayload(BaseModel):
    field: str = Field(min_length=1, max_length=50)
    reason: str = Field(min_length=5, max_length=2000)
    submitted_value: Optional[str] = None
    document_value: Optional[str] = None
    source_value: Optional[str] = None
    response_due_date: Optional[str] = None

@router.post("/api/submissions/{submission_id}/discrepancies", response_model=DiscrepancyResponse)
def issue_discrepancy(
    submission_id: str,
    payload: IssueDiscrepancyPayload,
    current_user: User = Depends(require_officer_user),
    db: Session = Depends(get_db)
):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if sub.review_status == "ACCEPTED":
        raise HTTPException(status_code=409, detail="Accepted instruments cannot receive new discrepancy queries.")
    open_existing = db.query(Discrepancy).filter(
        Discrepancy.submission_id == sub.id,
        Discrepancy.field == payload.field,
        Discrepancy.resolution.is_(None)
    ).first()
    if open_existing:
        raise HTTPException(status_code=409, detail="An unresolved query already exists for this field.")
    record = Discrepancy(
        id=f"DISC-{uuid.uuid4().hex[:8].upper()}",
        submission_id=sub.id,
        field=payload.field,
        submitted_value=payload.submitted_value,
        document_value=payload.document_value,
        source_value=payload.source_value,
        reason=payload.reason,
        assigned_to="COLLEGE",
        created_at=clock_service.now_iso(),
        response_due_date=payload.response_due_date,
    )
    db.add(record)
    sub.review_status = "CLARIFICATION_REQUIRED"
    db.commit()
    db.refresh(record)
    log_audit_event(
        db=db,
        entity_type="discrepancy",
        entity_id=record.id,
        actor_id=current_user.id,
        action="DISCREPANCY_QUERY_ISSUED",
        after_state={"field": record.field, "reason": record.reason, "assigned_to": record.assigned_to},
    )
    return DiscrepancyResponse.model_validate(record)

@router.get("/api/submissions/{submission_id}/discrepancies", response_model=List[DiscrepancyResponse])
def get_submission_discrepancies(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found.")

    verify_institution_access(sub.institution_id, current_user)
    discs = db.query(Discrepancy).filter(Discrepancy.submission_id == submission_id).all()
    return [DiscrepancyResponse.model_validate(d) for d in discs]

@router.post("/api/discrepancies/{discrepancy_id}/respond")
def respond_to_discrepancy(
    discrepancy_id: str,
    payload: CollegeResponsePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    disc = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found.")

    if current_user.role != "COLLEGE":
        raise HTTPException(status_code=403, detail="Only the institution representative can respond to a discrepancy.")
    if disc.resolution is not None:
        raise HTTPException(status_code=409, detail="This discrepancy has already been resolved.")
    sub = db.query(Submission).filter(Submission.id == disc.submission_id).first()
    if sub:
        verify_institution_access(sub.institution_id, current_user)

    disc.college_response = payload.response
    disc.response_submitted_at = clock_service.now_iso()
    disc.assigned_to = "OFFICER"
    db.commit()

    log_audit_event(
        db=db,
        entity_type="discrepancy",
        entity_id=disc.id,
        actor_id=current_user.id,
        action="DISCREPANCY_RESPONSE_SUBMITTED",
        after_state={"response": payload.response}
    )

    return {"message": "Clarification response submitted. Routed to AICTE Scrutiny Officer."}

@router.post("/api/discrepancies/{discrepancy_id}/resolve")
def resolve_discrepancy(
    discrepancy_id: str,
    payload: ResolveDiscrepancyPayload,
    current_user: User = Depends(require_officer_user),
    db: Session = Depends(get_db)
):
    disc = db.query(Discrepancy).filter(Discrepancy.id == discrepancy_id).first()
    if not disc:
        raise HTTPException(status_code=404, detail="Discrepancy not found.")

    if disc.resolution is not None:
        raise HTTPException(status_code=409, detail="This discrepancy has already been resolved.")
    if payload.resolution not in ("RESOLVED_ACCEPTED", "RESOLVED_REJECTED"):
        raise HTTPException(status_code=422, detail="Resolution must be RESOLVED_ACCEPTED or RESOLVED_REJECTED.")
    disc.resolution = payload.resolution
    disc.resolved_by = current_user.id
    disc.resolved_at = clock_service.now_iso()
    db.commit()

    # If all discrepancies resolved on submission, update status
    sub = db.query(Submission).filter(Submission.id == disc.submission_id).first()
    if sub:
        open_count = db.query(Discrepancy).filter(
            Discrepancy.submission_id == sub.id,
            Discrepancy.resolution.is_(None)
        ).count()
        rejected_count = db.query(Discrepancy).filter(
            Discrepancy.submission_id == sub.id,
            Discrepancy.resolution == "RESOLVED_REJECTED",
        ).count()
        if open_count == 0:
            if sub.review_status == "CLARIFICATION_REQUIRED":
                sub.review_status = "UNDER_REVIEW"
            if rejected_count == 0 and sub.verification_status == "MISMATCH":
                sub.verification_status = "CONFIRMED"
            db.commit()

    log_audit_event(
        db=db,
        entity_type="discrepancy",
        entity_id=disc.id,
        actor_id=current_user.id,
        action="DISCREPANCY_RESOLVED",
        after_state={"resolution": payload.resolution}
    )

    return {"message": f"Discrepancy marked as {payload.resolution}."}
