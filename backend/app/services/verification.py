import uuid, json
from typing import Dict, Any, Tuple
import httpx
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.clock import clock_service
from backend.app.models.models import Submission, BankVerification, User
from backend.app.services.audit import log_audit_event
from mock_bank.app.main import app as mock_bank_asgi_app
from fastapi.testclient import TestClient

def dispatch_bank_verification_request(bank_id: str, fdr_number: str) -> Tuple[int, Dict[str, Any]]:
    base_url = settings.MOCK_BANK_SERVICE_URL.rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"
    url = f"{base_url}/mock-bank/v1/fdr-verifications"
    headers = {"X-Service-Token": settings.BANK_SERVICE_TOKEN}
    payload = {"bank_id": bank_id, "fdr_number": fdr_number}

    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            return resp.status_code, resp.json() if resp.status_code != 503 else {"detail": "SOURCE_UNAVAILABLE"}
    except Exception:
        internal_client = TestClient(mock_bank_asgi_app)
        resp = internal_client.post("/mock-bank/v1/fdr-verifications", json=payload, headers=headers)
        if resp.status_code == 503:
            return 503, {"detail": "SOURCE_UNAVAILABLE"}
        return resp.status_code, resp.json()

def execute_bank_verification(db: Session, submission: Submission, actor_id: str) -> BankVerification:
    bank_id = submission.entered_bank_id or "DEMO-BANK-01"
    fdr_number = submission.entered_fdr_number

    req_time = clock_service.now_iso()
    status_code, data = dispatch_bank_verification_request(bank_id, fdr_number)
    resp_time = clock_service.now_iso()

    unique_suffix = uuid.uuid4().hex[:10].upper()
    verif_id = f"VERIF-{unique_suffix}"

    if status_code == 503:
        attempt = BankVerification(
            id=verif_id,
            submission_id=submission.id,
            verification_id=f"VBANK-OUTAGE-{unique_suffix[:6]}",
            bank_id=bank_id,
            fdr_number=fdr_number,
            method="SIMULATED_BANK_API",
            environment="MOCK",
            lookup_status="SOURCE_UNAVAILABLE",
            requested_at=req_time,
            responded_at=resp_time,
            status_as_of=None,
            confirmed_fields_json="{}",
            unsupported_fields_json="[]",
            source_reference=f"OUTAGE-REF-{unique_suffix[:6]}",
            evidence_note="Bank CBS gateway outage simulated (HTTP 503). Retained in retry queue.",
            recorded_by=actor_id
        )
        submission.verification_status = "SOURCE_UNAVAILABLE"

    elif data.get("lookup_status") == "NOT_FOUND":
        attempt = BankVerification(
            id=verif_id,
            submission_id=submission.id,
            verification_id=data.get("verification_id", verif_id),
            bank_id=bank_id,
            fdr_number=fdr_number,
            method="SIMULATED_BANK_API",
            environment="MOCK",
            lookup_status="NOT_FOUND",
            requested_at=req_time,
            responded_at=resp_time,
            status_as_of=None,
            confirmed_fields_json="{}",
            unsupported_fields_json="[]",
            source_reference=data.get("source_reference", "NOT_FOUND_REF"),
            evidence_note="Bank core returned NOT_FOUND. Routed to scrutiny.",
            recorded_by=actor_id
        )
        submission.verification_status = "MISMATCH"

    elif data.get("lookup_status") == "MANUAL_REQUIRED":
        attempt = BankVerification(
            id=verif_id,
            submission_id=submission.id,
            verification_id=data.get("verification_id", verif_id),
            bank_id=bank_id,
            fdr_number=fdr_number,
            method="SIMULATED_BANK_API",
            environment="MOCK",
            lookup_status="MANUAL_REQUIRED",
            requested_at=req_time,
            responded_at=resp_time,
            status_as_of=None,
            confirmed_fields_json="{}",
            unsupported_fields_json="[]",
            source_reference=data.get("source_reference", "MANUAL_REF"),
            evidence_note="Bank core requires manual branch verification.",
            recorded_by=actor_id
        )
        submission.verification_status = "MANUAL_REQUIRED"

    else:
        confirmed = data.get("confirmed_fields", {})
        unsupported = data.get("unsupported_fields", [])
        lookup_st = "PARTIAL" if unsupported else "FOUND"

        attempt = BankVerification(
            id=verif_id,
            submission_id=submission.id,
            verification_id=data.get("verification_id", verif_id),
            bank_id=bank_id,
            fdr_number=fdr_number,
            method="SIMULATED_BANK_API",
            environment="MOCK",
            lookup_status=lookup_st,
            requested_at=req_time,
            responded_at=resp_time,
            status_as_of=data.get("status_as_of"),
            confirmed_fields_json=json.dumps(confirmed),
            unsupported_fields_json=json.dumps(unsupported),
            source_reference=data.get("source_reference", "CBS-REF"),
            evidence_note="Bank confirmation received successfully." if not unsupported else "Partial fields confirmed by bank CBS.",
            recorded_by=actor_id
        )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    db.refresh(submission)

    log_audit_event(
        db=db,
        entity_type="bank_verification",
        entity_id=attempt.id,
        actor_id=actor_id,
        action="BANK_VERIFICATION_ATTEMPTED",
        after_state={"lookup_status": attempt.lookup_status, "fdr_number": fdr_number},
        source_reference=attempt.source_reference
    )
    return attempt
