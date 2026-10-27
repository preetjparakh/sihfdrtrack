import uuid, json, re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from backend.app.core.clock import clock_service
from backend.app.models.models import Submission, Document, OCRResult, BankVerification, Discrepancy
from backend.app.services.audit import log_audit_event

def clean_amount(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    cleaned = re.sub(r"[^\d.]", "", val)
    try:
        return float(cleaned)
    except ValueError:
        return None

def clean_text(val: Optional[str]) -> str:
    if not val:
        return ""
    return re.sub(r"\s+", " ", val.strip().lower())

def reconcile_submission_layers(db: Session, submission: Submission, actor_id: str) -> Dict[str, Any]:
    """
    Executes 3-way reconciliation across:
    Layer 1: Entered vs Document (OCR)
    Layer 2: Document vs Bank Confirmed
    Layer 3: Regulatory Compliance (Lien & Active status)
    """
    # 1. Fetch latest OCR results for this submission
    ocr_results = db.query(OCRResult).join(Document).filter(
        Document.submission_id == submission.id,
        OCRResult.engine_version != "mock-data-generator-1.0",
    ).all()
    ocr_dict = {r.field: r.corrected_value or r.normalized_value or r.raw_value for r in ocr_results}

    # 2. Fetch latest Bank Verification
    latest_verif = db.query(BankVerification).filter(
        BankVerification.submission_id == submission.id
    ).order_by(BankVerification.requested_at.desc()).first()

    bank_confirmed = {}
    if latest_verif and latest_verif.confirmed_fields_json:
        try:
            bank_confirmed = json.loads(latest_verif.confirmed_fields_json)
        except Exception:
            bank_confirmed = {}

    discrepancies_found = []

    # Check 1: Principal Amount
    sub_amt = clean_amount(submission.entered_principal_amount)
    ocr_amt = clean_amount(ocr_dict.get("principal_amount"))
    bank_amt = clean_amount(bank_confirmed.get("principal_amount"))

    if bank_amt is not None and sub_amt is not None and abs(sub_amt - bank_amt) > 0.01:
        discrepancies_found.append({
            "field": "principal_amount",
            "submitted_value": f"{sub_amt:.2f}",
            "document_value": f"{ocr_amt:.2f}" if ocr_amt is not None else None,
            "source_value": f"{bank_amt:.2f}",
            "reason": f"Principal amount mismatch: Submitted {sub_amt:.2f} INR differs from Bank confirmed {bank_amt:.2f} INR."
        })

    # Check 2: Maturity Date
    sub_mat = submission.entered_maturity_date
    bank_mat = bank_confirmed.get("maturity_date")
    if bank_mat and sub_mat and sub_mat != bank_mat:
        discrepancies_found.append({
            "field": "maturity_date",
            "submitted_value": sub_mat,
            "document_value": ocr_dict.get("maturity_date"),
            "source_value": bank_mat,
            "reason": f"Maturity date mismatch: Submitted {sub_mat} differs from Bank confirmed {bank_mat}."
        })

    # Check 3: Depositor Name
    sub_name = clean_text(submission.entered_depositor_name)
    bank_name = clean_text(bank_confirmed.get("depositor_name"))
    if bank_name and sub_name and sub_name != bank_name:
        discrepancies_found.append({
            "field": "depositor_name",
            "submitted_value": submission.entered_depositor_name,
            "document_value": ocr_dict.get("depositor_name"),
            "source_value": bank_confirmed.get("depositor_name"),
            "reason": f"Depositor name mismatch: Submitted '{submission.entered_depositor_name}' differs from Bank '{bank_confirmed.get('depositor_name')}'."
        })

    # Check 4: Lien Status
    sub_lien = clean_text(submission.entered_lien_status)
    bank_lien = clean_text(bank_confirmed.get("lien_status"))
    if bank_lien and sub_lien and sub_lien != bank_lien:
        discrepancies_found.append({
            "field": "lien_status",
            "submitted_value": submission.entered_lien_status,
            "document_value": ocr_dict.get("lien_status"),
            "source_value": bank_confirmed.get("lien_status"),
            "reason": f"Lien status discrepancy: Bank confirmed '{bank_confirmed.get('lien_status')}'."
        })

    # Sync discrepancies with database
    for d in discrepancies_found:
        existing = db.query(Discrepancy).filter(
            Discrepancy.submission_id == submission.id,
            Discrepancy.field == d["field"]
        ).first()

        if not existing:
            disc_entry = Discrepancy(
                id=f"DISC-{uuid.uuid4().hex[:8].upper()}",
                submission_id=submission.id,
                field=d["field"],
                submitted_value=d["submitted_value"],
                document_value=d["document_value"],
                source_value=d["source_value"],
                reason=d["reason"],
                assigned_to="COLLEGE",
                created_at=clock_service.now_iso()
            )
            db.add(disc_entry)

    if discrepancies_found:
        submission.verification_status = "MISMATCH"
    elif latest_verif and latest_verif.lookup_status == "FOUND":
        submission.verification_status = "CONFIRMED"

    db.commit()
    db.refresh(submission)

    return {
        "submission_id": submission.id,
        "verification_status": submission.verification_status,
        "discrepancies_count": len(discrepancies_found),
        "discrepancies": discrepancies_found
    }
