import io
import hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.models import Document, OCRResult, AuditLog

client = TestClient(app)

def test_document_upload_and_generated_mock_extraction():
    # 1. Create a draft submission for College A (USER-C01, INST-001)
    create_resp = client.post(
        "/api/submissions",
        json={
            "application_reference": "TEST-APP-001",
            "bank_id": "DEMO-BANK-01",
            "fdr_number": "FDR-2026-000001",
            "depositor_name": "Aarav Sharma",
            "principal_amount": "1000000.00",
            "currency": "INR",
            "issue_date": "2026-01-15",
            "maturity_date": "2027-04-24"
        },
        headers={"X-Demo-User-Id": "USER-C01"}
    )
    assert create_resp.status_code == 200
    sub_data = create_resp.json()
    sub_id = sub_data["id"]
    assert sub_data["review_status"] == "DRAFT"

    # 2. Upload DOC-001.png to this submission
    fixture_path = Path("fixtures/DOC-001.png")
    with open(fixture_path, "rb") as f:
        file_bytes = f.read()

    upload_resp = client.post(
        f"/api/submissions/{sub_id}/documents",
        files={"file": ("DOC-001.png", io.BytesIO(file_bytes), "image/png")},
        data={"doc_type": "FDR_RECEIPT"},
        headers={"X-Demo-User-Id": "USER-C01"}
    )
    assert upload_resp.status_code == 200
    doc_data = upload_resp.json()
    doc_id = doc_data["id"]
    assert doc_data["filename"] == "DOC-001.png"

    # Verify SHA-256 matches actual bytes
    expected_hash = hashlib.sha256(file_bytes).hexdigest()
    assert doc_data["sha256"] == expected_hash

    # 3. Retrieve OCR results for this document
    ocr_resp = client.get(
        f"/api/documents/{doc_id}/ocr",
        headers={"X-Demo-User-Id": "USER-C01"}
    )
    assert ocr_resp.status_code == 200
    ocr_list = ocr_resp.json()
    assert len(ocr_list) == 10
    assert all(result["review_status"] == "MOCK_GENERATED" for result in ocr_list)
    assert all(result["engine_version"] == "mock-data-generator-1.0" for result in ocr_list)

    # Check extracted fdr_number and principal_amount
    fdr_ocr = next((r for r in ocr_list if r["field"] == "fdr_number"), None)
    assert fdr_ocr is not None
    assert fdr_ocr["raw_value"].startswith("FDR-2026-")
    assert fdr_ocr["confidence"] is not None
    assert fdr_ocr["review_status"] == "MOCK_GENERATED"

    # 4. Correct an OCR field (e.g. depositor_name)
    correct_resp = client.put(
        f"/api/ocr-results/{fdr_ocr['id']}/correct",
        json={"corrected_value": "FDR-2026-000001", "reason": "Officer visual check confirmed zero digit"},
        headers={"X-Demo-User-Id": "USER-C01"}
    )
    assert correct_resp.status_code == 200
    updated_ocr = correct_resp.json()
    assert updated_ocr["corrected_value"] == "FDR-2026-000001"
    assert updated_ocr["review_status"] == "CORRECTED"

    # 5. Finalize submission
    submit_resp = client.post(
        f"/api/submissions/{sub_id}/submit",
        headers={"X-Demo-User-Id": "USER-C01"}
    )
    assert submit_resp.status_code == 200
    submit_data = submit_resp.json()
    assert submit_data["review_status"] == "SUBMITTED"
    assert "ACK-" in submit_data["acknowledgement_id"]
    assert submit_data["assigned_officer_id"] == "USER-O01"

def test_document_download_isolation():
    """
    Acceptance Check 1: College B cannot download College A's document.
    """
    # Find a document belonging to College A (INST-001, e.g. DOC-001)
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == "DOC-001").first()
    db.close()
    assert doc is not None

    # College B rep (USER-C02) attempts to download DOC-001
    resp_unauthorized = client.get(
        f"/api/documents/DOC-001/file",
        headers={"X-Demo-User-Id": "USER-C02"}
    )
    assert resp_unauthorized.status_code == 403

    # Officer (USER-O01) can download DOC-001
    resp_officer = client.get(
        f"/api/documents/DOC-001/file",
        headers={"X-Demo-User-Id": "USER-O01"}
    )
    assert resp_officer.status_code == 200
    assert len(resp_officer.content) > 0


@pytest.mark.parametrize("content_type", ["application/pdf", "application/octet-stream"])
def test_pdf_upload_uses_document_route_and_generates_mock_values(content_type):
    create_resp = client.post(
        "/api/submissions",
        json={
            "application_reference": f"TEST-PDF-APP-{content_type.replace('/', '-')}",
            "bank_id": "DEMO-BANK-01",
            "fdr_number": "TEST-PDF-FDR",
            "depositor_name": "Synthetic College",
            "principal_amount": "500000.00",
            "currency": "INR",
            "issue_date": "2026-01-15",
            "maturity_date": "2027-04-24",
        },
        headers={"X-Demo-User-Id": "USER-C01"},
    )
    assert create_resp.status_code == 200
    submission_id = create_resp.json()["id"]

    fixture_path = Path("fixtures/DOC-001.pdf")
    with fixture_path.open("rb") as document_file:
        upload_resp = client.post(
            f"/api/submissions/{submission_id}/documents",
            files={"file": (fixture_path.name, document_file, content_type)},
            headers={"X-Demo-User-Id": "USER-C01"},
        )
    assert upload_resp.status_code == 200

    doc_id = upload_resp.json()["id"]
    ocr_resp = client.get(
        f"/api/documents/{doc_id}/ocr",
        headers={"X-Demo-User-Id": "USER-C01"},
    )
    assert ocr_resp.status_code == 200
    assert len(ocr_resp.json()) == 10
    assert all(row["engine_version"] == "mock-data-generator-1.0" for row in ocr_resp.json())
