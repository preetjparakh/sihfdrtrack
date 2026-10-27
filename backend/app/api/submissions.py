import uuid
import hashlib
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.clock import clock_service
from backend.app.api.deps import get_current_user, verify_institution_access
from backend.app.models.models import User, Submission, Document, OCRResult, Discrepancy, BankVerification, ReleaseRequest, Renewal
from backend.app.schemas.schemas import SubmissionResponse, SubmissionDetailResponse
from backend.app.services.audit import log_audit_event

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

class SubmissionCreateRequest(BaseModel):
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
    predecessor_submission_id: Optional[str] = None

class SubmissionSubmitResponse(BaseModel):
    acknowledgement_id: str
    submission_id: str
    application_reference: str
    submitted_at: str
    assigned_officer_id: str
    review_status: str
    duplicate_reference_warning: bool = False
    message: str

class SubmissionRejectionRequest(BaseModel):
    reason: str

@router.get("", response_model=List[SubmissionResponse])
def list_submissions(
    review_status: Optional[str] = Query(None),
    verification_status: Optional[str] = Query(None),
    institution_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Submission)
    if current_user.role == "COLLEGE":
        query = query.filter(Submission.institution_id == current_user.institution_id)
    elif institution_id:
        query = query.filter(Submission.institution_id == institution_id)

    if review_status:
        query = query.filter(Submission.review_status == review_status)
    if verification_status:
        query = query.filter(Submission.verification_status == verification_status)

    submissions = query.order_by(Submission.id.asc()).all()
    return [SubmissionResponse.model_validate(s) for s in submissions]

@router.post("", response_model=SubmissionResponse)
def create_submission(
    payload: SubmissionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "COLLEGE" or not current_user.institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authenticated college representatives can create submissions."
        )

    sub_id = f"SUB-{uuid.uuid4().hex[:8].upper()}"
    now_iso = clock_service.now_iso()

    sub = Submission(
        id=sub_id,
        institution_id=current_user.institution_id,
        scenario="CUSTOM",
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
        entered_status_as_of=now_iso,
        entered_record_updated_at=now_iso,
        review_status="DRAFT",
        verification_status="NOT_INITIATED",
        submitted_at=now_iso,
        assigned_officer_id="USER-O01",
        predecessor_submission_id=payload.predecessor_submission_id
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    log_audit_event(
        db=db,
        entity_type="submission",
        entity_id=sub.id,
        actor_id=current_user.id,
        action="SUBMISSION_DRAFT_CREATED",
        after_state={"fdr_number": sub.entered_fdr_number, "amount": sub.entered_principal_amount}
    )

    return SubmissionResponse.model_validate(sub)

@router.post("/{submission_id}/submit", response_model=SubmissionSubmitResponse)
def finalize_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if current_user.role != "COLLEGE":
        raise HTTPException(status_code=403, detail="Only institution representatives can finalize submissions.")
    verify_institution_access(submission.institution_id, current_user)

    ack_id = f"ACK-{hashlib.sha256(submission.id.encode('utf-8')).hexdigest()[:10].upper()}"
    if submission.review_status == "SUBMITTED":
        return SubmissionSubmitResponse(
            acknowledgement_id=ack_id,
            submission_id=submission.id,
            application_reference=submission.application_reference,
            submitted_at=submission.submitted_at,
            assigned_officer_id=submission.assigned_officer_id or "USER-O01",
            review_status=submission.review_status,
            message="This submission was already finalized. The original acknowledgement is unchanged.",
        )
    if submission.review_status != "DRAFT":
        raise HTTPException(status_code=409, detail="Only a draft submission can be finalized.")

    # Check documents: must have at least one uploaded document
    doc_count = db.query(Document).filter(Document.submission_id == submission_id).count()
    if doc_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission cannot be submitted without at least one uploaded instrument document."
        )

    # Check duplicate reference warning (composite bank_id + fdr_number)
    duplicate_count = db.query(Submission).filter(
        Submission.id != submission_id,
        Submission.entered_bank_id == submission.entered_bank_id,
        Submission.entered_fdr_number == submission.entered_fdr_number
    ).count()

    is_duplicate = (duplicate_count > 0)
    now_iso = clock_service.now_iso()

    submission.review_status = "SUBMITTED"
    submission.submitted_at = now_iso
    submission.assigned_officer_id = "USER-O01"
    db.commit()
    db.refresh(submission)

    log_audit_event(
        db=db,
        entity_type="submission",
        entity_id=submission.id,
        actor_id=current_user.id,
        action="SUBMISSION_FINALIZED_AND_FROZEN",
        after_state={"review_status": "SUBMITTED", "ack_id": ack_id, "duplicate_warning": is_duplicate}
    )

    msg = "Submission received and frozen. Routed to AICTE Scrutiny Officer."
    if is_duplicate:
        msg += " Warning: A duplicate FDR reference was detected for this bank. Case flagged for officer scrutiny."

    return SubmissionSubmitResponse(
        acknowledgement_id=ack_id,
        submission_id=submission.id,
        application_reference=submission.application_reference,
        submitted_at=now_iso,
        assigned_officer_id="USER-O01",
        review_status="SUBMITTED",
        duplicate_reference_warning=is_duplicate,
        message=msg
    )

@router.get("/{submission_id}", response_model=SubmissionDetailResponse)
def get_submission_detail(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {submission_id} not found."
        )

    verify_institution_access(submission.institution_id, current_user)

    return SubmissionDetailResponse.model_validate(submission)

@router.post("/{submission_id}/start-review")
def start_submission_review(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "OFFICER":
        raise HTTPException(status_code=403, detail="Only AICTE Scrutiny Officers can start a review.")

    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if submission.review_status != "SUBMITTED":
        raise HTTPException(status_code=409, detail="Only a newly submitted instrument can enter review.")

    before_status = submission.review_status
    submission.review_status = "UNDER_REVIEW"
    db.commit()
    db.refresh(submission)
    log_audit_event(
        db, "submission", submission.id, current_user.id, "SUBMISSION_REVIEW_STARTED",
        before_state={"review_status": before_status},
        after_state={"review_status": submission.review_status},
    )
    return {"submission_id": submission.id, "review_status": submission.review_status}

@router.post("/{submission_id}/reject")
def reject_submission(
    submission_id: str,
    payload: SubmissionRejectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "OFFICER":
        raise HTTPException(status_code=403, detail="Only AICTE Scrutiny Officers can reject submissions.")
    reason = payload.reason.strip()
    if len(reason) < 5:
        raise HTTPException(status_code=422, detail="A rejection reason of at least five characters is required.")

    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if submission.review_status not in ("SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"):
        raise HTTPException(status_code=409, detail="Only a submission under scrutiny can be rejected.")

    before_status = submission.review_status
    submission.review_status = "REJECTED"
    db.commit()
    db.refresh(submission)
    log_audit_event(
        db, "submission", submission.id, current_user.id, "SUBMISSION_REJECTED_BY_OFFICER",
        before_state={"review_status": before_status},
        after_state={"review_status": submission.review_status},
        reason=reason,
    )
    return {"submission_id": submission.id, "review_status": submission.review_status, "reason": reason}

@router.post("/{submission_id}/accept")
def accept_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "OFFICER":
        raise HTTPException(status_code=403, detail="Only AICTE Scrutiny Officers can accept submissions.")

    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if submission.review_status not in ("SUBMITTED", "UNDER_REVIEW", "CLARIFICATION_REQUIRED"):
        raise HTTPException(status_code=409, detail="Only a submitted instrument can be accepted.")
    if db.query(Document).filter(Document.submission_id == submission.id).count() == 0:
        raise HTTPException(status_code=400, detail="A submitted instrument document is required before acceptance.")

    open_discs = db.query(Discrepancy).filter(
        Discrepancy.submission_id == submission_id,
        Discrepancy.resolution.is_(None)
    ).count()

    if open_discs > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot accept submission with {open_discs} unresolved discrepancies. Resolve all queries first."
        )

    before_status = submission.review_status
    if submission.verification_status != "CONFIRMED":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot accept submission until verification is CONFIRMED (current: {submission.verification_status})."
        )

    submission.review_status = "ACCEPTED"
    renewal = db.query(Renewal).filter(
        Renewal.successor_submission_id == submission.id,
        Renewal.status == "PENDING",
    ).first()
    if renewal:
        predecessor = db.query(Submission).filter(
            Submission.id == renewal.predecessor_submission_id
        ).first()
        if predecessor:
            predecessor.entered_instrument_status = "SUPERSEDED"
        renewal.status = "ACCEPTED"
    db.commit()
    db.refresh(submission)

    log_audit_event(
        db=db,
        entity_type="submission",
        entity_id=submission.id,
        actor_id=current_user.id,
        action="SUBMISSION_ACCEPTED_BY_OFFICER",
        before_state={"review_status": before_status},
        after_state={"review_status": "ACCEPTED"}
    )

    if renewal:
        log_audit_event(
            db=db,
            entity_type="renewal",
            entity_id=renewal.id,
            actor_id=current_user.id,
            action="SUCCESSOR_ACCEPTED_PREDECESSOR_SUPERSEDED",
            before_state={"renewal_status": "PENDING", "predecessor_status": "ACTIVE"},
            after_state={"renewal_status": "ACCEPTED", "predecessor_status": "SUPERSEDED"},
        )

    return {
        "message": f"Submission {submission_id} accepted successfully.",
        "review_status": "ACCEPTED",
        "renewal_status": renewal.status if renewal else None,
    }
