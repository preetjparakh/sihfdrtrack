import os
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from mock_bank.app.database import get_bank_db
from mock_bank.app.models import MockBankRecord

BANK_SERVICE_TOKEN = os.getenv("BANK_SERVICE_TOKEN", "demo-bank-s2s-token-secure-394872190")

app = FastAPI(
    title="AICTE Synthetic Bank Verification Service",
    description="Authoritative mock bank FDR verification endpoint enforcing fixture scenarios independently.",
    version="1.0"
)

class VerificationRequest(BaseModel):
    bank_id: str = Field(..., example="DEMO-BANK-01")
    fdr_number: str = Field(..., example="FDR-2026-000001")

class VerificationResponse(BaseModel):
    verification_id: str
    environment: str = "MOCK"
    source: str
    lookup_status: str  # FOUND, NOT_FOUND, SOURCE_UNAVAILABLE, MANUAL_REQUIRED
    requested_at: str
    responded_at: str
    status_as_of: Optional[str] = None
    confirmed_fields: Dict[str, Any] = {}
    unsupported_fields: List[str] = []
    source_reference: str

def verify_s2s_auth(x_service_token: Optional[str] = Header(None, alias="X-Service-Token")):
    if not x_service_token or x_service_token != BANK_SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized service request: Invalid or missing X-Service-Token."
        )
    return True

@app.get("/health")
def health():
    return {"status": "ok", "service": "mock-bank", "environment": "MOCK"}

@app.post("/mock-bank/v1/fdr-verifications", response_model=VerificationResponse)
def verify_fdr(
    payload: VerificationRequest,
    authenticated: bool = Depends(verify_s2s_auth),
    db: Session = Depends(get_bank_db)
):
    requested_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    verification_id = f"VBANK-{uuid.uuid4().hex[:10].upper()}"
    source_ref = f"CBS-DEMO-{uuid.uuid4().hex[:8].upper()}"

    # Fixed fixture behaviors as required by specification:
    # 1. SUB-006: SOURCE_UNAVAILABLE -> HTTP 503
    if payload.fdr_number == "FDR-2026-000006":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bank CBS Core Gateway Unavailable. Outage simulated for SUB-006."
        )

    # 2. SUB-005: NOT_FOUND
    if payload.fdr_number == "FDR-2026-000005":
        responded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return VerificationResponse(
            verification_id=verification_id,
            environment="MOCK",
            source=payload.bank_id,
            lookup_status="NOT_FOUND",
            requested_at=requested_at,
            responded_at=responded_at,
            status_as_of=None,
            confirmed_fields={},
            unsupported_fields=[],
            source_reference=source_ref
        )

    # 3. SUB-027: MANUAL_REQUIRED
    if payload.fdr_number == "FDR-2026-000027":
        responded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return VerificationResponse(
            verification_id=verification_id,
            environment="MOCK",
            source=payload.bank_id,
            lookup_status="MANUAL_REQUIRED",
            requested_at=requested_at,
            responded_at=responded_at,
            status_as_of=None,
            confirmed_fields={},
            unsupported_fields=[],
            source_reference=source_ref
        )

    # Look up authoritative record in mock_bank_records
    record = db.query(MockBankRecord).filter(
        MockBankRecord.bank_id == payload.bank_id,
        MockBankRecord.fdr_number == payload.fdr_number
    ).first()

    responded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not record:
        return VerificationResponse(
            verification_id=verification_id,
            environment="MOCK",
            source=payload.bank_id,
            lookup_status="NOT_FOUND",
            requested_at=requested_at,
            responded_at=responded_at,
            status_as_of=None,
            confirmed_fields={},
            unsupported_fields=[],
            source_reference=source_ref
        )

    # 4. SUB-007: PARTIAL_RESPONSE -> omit lien fields, list in unsupported_fields
    if payload.fdr_number == "FDR-2026-000007":
        confirmed = {
            "fdr_number": record.fdr_number,
            "depositor_name": record.depositor_name,
            "principal_amount": record.principal_amount,
            "currency": record.currency,
            "issue_date": record.issue_date,
            "maturity_date": record.maturity_date,
            "instrument_status": record.instrument_status,
            "beneficiary_name": record.beneficiary_name,
        }
        unsupported = ["lien_status", "lien_in_favour_of"]
        return VerificationResponse(
            verification_id=verification_id,
            environment="MOCK",
            source=payload.bank_id,
            lookup_status="FOUND",
            requested_at=requested_at,
            responded_at=responded_at,
            status_as_of=record.status_as_of,
            confirmed_fields=confirmed,
            unsupported_fields=unsupported,
            source_reference=source_ref
        )

    # Standard existing record response
    confirmed = {
        "fdr_number": record.fdr_number,
        "depositor_name": record.depositor_name,
        "principal_amount": record.principal_amount,
        "currency": record.currency,
        "issue_date": record.issue_date,
        "maturity_date": record.maturity_date,
        "instrument_status": record.instrument_status,
        "beneficiary_name": record.beneficiary_name,
        "lien_status": record.lien_status,
        "lien_in_favour_of": record.lien_in_favour_of,
    }

    return VerificationResponse(
        verification_id=verification_id,
        environment="MOCK",
        source=payload.bank_id,
        lookup_status="FOUND",
        requested_at=requested_at,
        responded_at=responded_at,
        status_as_of=record.status_as_of,
        confirmed_fields=confirmed,
        unsupported_fields=[],
        source_reference=source_ref
    )
