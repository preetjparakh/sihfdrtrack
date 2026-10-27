import json, uuid
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.clock import clock_service
from backend.app.api.deps import get_current_user, require_officer_user, verify_institution_access
from backend.app.models.models import User, Submission, BankVerification, ManualConfirmation
from backend.app.services.verification import execute_bank_verification
from backend.app.services.comparison import reconcile_submission_layers
from backend.app.services.audit import log_audit_event

router = APIRouter(prefix="/api/submissions", tags=["verification"])

class ManualConfirmRequest(BaseModel):
    contact_source: str
    evidence_doc_id: Optional[str] = None
    confirmed_fields: Dict[str, Any]
    notes: str

@router.post("/{submission_id}/verify-bank")
def trigger_bank_verification(
    submission_id: str,
    current_user: User = Depends(require_officer_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if submission.review_status == "ACCEPTED":
        raise HTTPException(status_code=409, detail="Accepted instruments cannot be re-verified.")

    attempt = execute_bank_verification(db, submission, current_user.id)
    recon = reconcile_submission_layers(db, submission, current_user.id)

    return {
        "message": "Bank verification executed.",
        "verification_attempt": {
            "id": attempt.id,
            "lookup_status": attempt.lookup_status,
            "source": attempt.bank_id,
            "source_reference": attempt.source_reference,
            "responded_at": attempt.responded_at
        },
        "reconciliation": recon
    }

@router.post("/{submission_id}/manual-confirm")
def record_manual_bank_confirmation(
    submission_id: str,
    payload: ManualConfirmRequest,
    current_user: User = Depends(require_officer_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if submission.verification_status not in ("MANUAL_REQUIRED", "SOURCE_UNAVAILABLE", "PARTIAL"):
        raise HTTPException(
            status_code=409,
            detail=f"Manual confirmation is unavailable for status {submission.verification_status}.",
        )

    manual_id = f"MCONF-{uuid.uuid4().hex[:8].upper()}"
    now_iso = clock_service.now_iso()

    record = ManualConfirmation(
        id=manual_id,
        submission_id=submission.id,
        officer_id=current_user.id,
        contact_source=payload.contact_source,
        evidence_doc_id=payload.evidence_doc_id,
        confirmed_fields_json=json.dumps(payload.confirmed_fields),
        confirmed_at=now_iso,
        notes=payload.notes
    )
    db.add(record)

    submission.verification_status = "CONFIRMED"
    db.commit()
    db.refresh(submission)

    log_audit_event(
        db=db,
        entity_type="manual_confirmation",
        entity_id=record.id,
        actor_id=current_user.id,
        action="MANUAL_CONFIRMATION_RECORDED",
        after_state={"contact_source": payload.contact_source, "confirmed_fields": payload.confirmed_fields},
        source_reference=payload.contact_source
    )

    return {
        "message": "Manual confirmation recorded successfully.",
        "id": record.id,
        "submission_id": submission.id,
        "verification_status": submission.verification_status,
        "confirmed_at": now_iso
    }
