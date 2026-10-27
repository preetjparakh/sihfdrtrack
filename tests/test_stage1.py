import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from mock_bank.app.main import app as mock_bank_app
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.models import Bank

client = TestClient(app)
bank_client = TestClient(mock_bank_app)

def test_health_and_clock():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["demo_clock"] == "2026-10-26T04:30:00Z"
    assert "26 October 2026 at 10:00 IST" in data["display_time"]
    assert data["synthetic_watermark"] == "SYNTHETIC - FOR PROTOTYPE ONLY"

def test_auth_personas():
    resp = client.get("/api/auth/personas")
    assert resp.status_code == 200
    personas = resp.json()
    assert len(personas) == 12

    # Check College A, Officer, Authority personas
    college_c01 = next(p for p in personas if p["id"] == "USER-C01")
    assert college_c01["role"] == "COLLEGE"
    assert college_c01["institution_id"] == "INST-001"
    assert college_c01["badge"] == "Aarav Sharma · College Representative"

    officer = next(p for p in personas if p["id"] == "USER-O01")
    assert officer["role"] == "OFFICER"

    approver = next(p for p in personas if p["id"] == "USER-A01")
    assert approver["role"] == "APPROVER"

def test_named_bank_catalog():
    expected_names = {
        "Aegis National Trust",
        "Vanguard Horizon Bank",
        "Crestview Commerce Bank",
        "Meridian Reserve Corp",
        "Silverline Federal Credit Union",
        "Solstice Merchant Bank",
    }
    db = SessionLocal()
    try:
        assert {bank.name for bank in db.query(Bank).all()} == expected_names
    finally:
        db.close()

def test_token_issuance_and_me():
    resp = client.post("/api/auth/token", json={"user_id": "USER-C01"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    token = data["access_token"]

    # Verify /me endpoint
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me = me_resp.json()
    assert me["id"] == "USER-C01"
    assert me["role"] == "COLLEGE"
    assert me["institution_id"] == "INST-001"

def test_cross_institution_isolation():
    """
    Acceptance Check 1: College A cannot list or view College B submissions.
    """
    # 1. College A lists submissions: all must belong to INST-001
    resp_a = client.get("/api/submissions", headers={"X-Demo-User-Id": "USER-C01"})
    assert resp_a.status_code == 200
    submissions_a = resp_a.json()
    assert len(submissions_a) > 0
    assert all(s["institution_id"] == "INST-001" for s in submissions_a)

    # 2. College A attempts to view College B submission SUB-002 (INST-002)
    resp_forbidden = client.get("/api/submissions/SUB-002", headers={"X-Demo-User-Id": "USER-C01"})
    assert resp_forbidden.status_code == 403
    assert "Access denied" in resp_forbidden.json()["detail"]

    # 3. Officer can list ALL submissions and view any submission detail
    resp_officer = client.get("/api/submissions", headers={"X-Demo-User-Id": "USER-O01"})
    assert resp_officer.status_code == 200
    all_subs = resp_officer.json()
    assert len(all_subs) == 30

    resp_officer_sub2 = client.get("/api/submissions/SUB-002", headers={"X-Demo-User-Id": "USER-O01"})
    assert resp_officer_sub2.status_code == 200
    assert resp_officer_sub2.json()["id"] == "SUB-002"

def test_dashboard_metrics_role_scoping():
    # College A dashboard (scoped to INST-001)
    resp_college = client.get("/api/dashboard", headers={"X-Demo-User-Id": "USER-C01"})
    assert resp_college.status_code == 200
    dash_c = resp_college.json()
    assert dash_c["total_submissions"] < 30
    assert dash_c["demo_clock"] == "2026-10-26T04:30:00Z"

    # Officer dashboard (global AICTE overview)
    resp_officer = client.get("/api/dashboard", headers={"X-Demo-User-Id": "USER-O01"})
    assert resp_officer.status_code == 200
    dash_o = resp_officer.json()
    assert dash_o["total_submissions"] == 30

def test_mock_bank_service_contract_and_scenarios():
    headers = {"X-Service-Token": settings.BANK_SERVICE_TOKEN}

    # 1. Unauthorized request
    bad_resp = bank_client.post("/mock-bank/v1/fdr-verifications", json={"bank_id": "DEMO-BANK-01", "fdr_number": "FDR-2026-000001"})
    assert bad_resp.status_code == 401

    # 2. SUB-001: Standard MATCH
    resp_match = bank_client.post(
        "/mock-bank/v1/fdr-verifications",
        json={"bank_id": "DEMO-BANK-01", "fdr_number": "FDR-2026-000001"},
        headers=headers
    )
    assert resp_match.status_code == 200
    data_match = resp_match.json()
    assert data_match["lookup_status"] == "FOUND"
    assert data_match["confirmed_fields"]["depositor_name"] == "Aarav Sharma"
    assert data_match["confirmed_fields"]["principal_amount"] == "1000000.00"
    assert data_match["confirmed_fields"]["maturity_date"] == "2027-04-24"

    # 3. SUB-005: NOT_FOUND
    resp_sub5 = bank_client.post(
        "/mock-bank/v1/fdr-verifications",
        json={"bank_id": "DEMO-BANK-01", "fdr_number": "FDR-2026-000005"},
        headers=headers
    )
    assert resp_sub5.status_code == 200
    assert resp_sub5.json()["lookup_status"] == "NOT_FOUND"

    # 4. SUB-006: SOURCE_UNAVAILABLE (503)
    resp_sub6 = bank_client.post(
        "/mock-bank/v1/fdr-verifications",
        json={"bank_id": "DEMO-BANK-01", "fdr_number": "FDR-2026-000006"},
        headers=headers
    )
    assert resp_sub6.status_code == 503

    # 5. SUB-007: PARTIAL_RESPONSE
    resp_sub7 = bank_client.post(
        "/mock-bank/v1/fdr-verifications",
        json={"bank_id": "DEMO-BANK-01", "fdr_number": "FDR-2026-000007"},
        headers=headers
    )
    assert resp_sub7.status_code == 200
    data_sub7 = resp_sub7.json()
    assert data_sub7["lookup_status"] == "FOUND"
    assert "lien_status" in data_sub7["unsupported_fields"]
    assert "lien_status" not in data_sub7["confirmed_fields"]

    # 6. SUB-027: MANUAL_REQUIRED
    resp_sub27 = bank_client.post(
        "/mock-bank/v1/fdr-verifications",
        json={"bank_id": "DEMO-BANK-03", "fdr_number": "FDR-2026-000027"},
        headers=headers
    )
    assert resp_sub27.status_code == 200
    assert resp_sub27.json()["lookup_status"] == "MANUAL_REQUIRED"
