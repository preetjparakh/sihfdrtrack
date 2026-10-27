import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import Submission, Discrepancy, BankVerification, ManualConfirmation

client = TestClient(app)

def test_bank_verification_and_comparison_scenarios():
    # 1. SUB-001: Clean Match
    resp_sub1 = client.post(
        "/api/submissions/SUB-001/verify-bank",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_sub1.status_code == 200
    data_sub1 = resp_sub1.json()
    assert data_sub1["verification_attempt"]["lookup_status"] == "FOUND"
    assert data_sub1["reconciliation"]["verification_status"] == "CONFIRMED"
    assert data_sub1["reconciliation"]["discrepancies_count"] == 0

    # 2. SUB-002: Amount Mismatch (10L submitted vs 15L bank confirmed)
    resp_sub2 = client.post(
        "/api/submissions/SUB-002/verify-bank",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_sub2.status_code == 200
    data_sub2 = resp_sub2.json()
    assert data_sub2["reconciliation"]["verification_status"] == "MISMATCH"
    assert data_sub2["reconciliation"]["discrepancies_count"] >= 1
    amount_disc = next(d for d in data_sub2["reconciliation"]["discrepancies"] if d["field"] == "principal_amount")
    assert amount_disc["submitted_value"] == "1500000.00"
    assert amount_disc["source_value"] == "1000000.00"

    # 3. SUB-005: Bank Record Not Found
    resp_sub5 = client.post(
        "/api/submissions/SUB-005/verify-bank",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_sub5.status_code == 200
    assert resp_sub5.json()["verification_attempt"]["lookup_status"] == "NOT_FOUND"

    # 4. SUB-006: Bank CBS Outage (503)
    resp_sub6 = client.post(
        "/api/submissions/SUB-006/verify-bank",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_sub6.status_code == 200
    assert resp_sub6.json()["verification_attempt"]["lookup_status"] == "SOURCE_UNAVAILABLE"

    # 5. SUB-007: Partial Response (Lien unsupported)
    resp_sub7 = client.post(
        "/api/submissions/SUB-007/verify-bank",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_sub7.status_code == 200
    assert resp_sub7.json()["verification_attempt"]["lookup_status"] == "PARTIAL"

def test_discrepancy_and_acceptance_lifecycle():
    # 1. Query discrepancies on SUB-002 (College B rep)
    resp_discs = client.get(
        "/api/submissions/SUB-002/discrepancies",
        headers={"X-Demo-User-Id": "USER-C02"}
    )
    assert resp_discs.status_code == 200
    discs = resp_discs.json()
    assert len(discs) > 0
    disc_id = discs[0]["id"]

    # 2. Officer cannot accept SUB-002 while discrepancy is unresolved
    resp_accept_blocked = client.post(
        "/api/submissions/SUB-002/accept",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_accept_blocked.status_code == 400
    assert "unresolved discrepancies" in resp_accept_blocked.json()["detail"]

    # 3. College responds to discrepancy
    resp_respond = client.post(
        f"/api/discrepancies/{disc_id}/respond",
        json={"response": "Acknowledged. Bank confirmed higher deposit of 15 Lakh which satisfies requirement."},
        headers={"X-Demo-User-Id": "USER-C02"}
    )
    assert resp_respond.status_code == 200

    # 4. Officer resolves discrepancy
    resp_resolve = client.post(
        f"/api/discrepancies/{disc_id}/resolve",
        json={"resolution": "RESOLVED_ACCEPTED"},
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_resolve.status_code == 200

    # 5. Officer now accepts SUB-002
    resp_accept = client.post(
        "/api/submissions/SUB-002/accept",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_accept.status_code == 200
    assert resp_accept.json()["review_status"] == "ACCEPTED"

def test_manual_confirmation_workflow():
    # Officer records manual confirmation for SUB-027 (FDR-2026-000027)
    resp_verify = client.post(
        "/api/submissions/SUB-027/verify-bank",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_verify.status_code == 200
    assert resp_verify.json()["verification_attempt"]["lookup_status"] == "MANUAL_REQUIRED"

    resp_manual = client.post(
        "/api/submissions/SUB-027/manual-confirm",
        json={
            "contact_source": "Branch Manager Official Contact: bm.branch3@syntheticbank.invalid",
            "evidence_doc_id": "DOC-BRANCH-CONFIRM-91",
            "confirmed_fields": {"principal_amount": "1000000.00", "maturity_date": "2027-04-24", "lien_status": "MARKED"},
            "notes": "Verified directly via branch manager official email with branch seal scan."
        },
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_manual.status_code == 200
    data = resp_manual.json()
    assert data["verification_status"] == "CONFIRMED"
