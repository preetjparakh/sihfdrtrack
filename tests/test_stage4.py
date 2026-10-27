import io
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.clock import clock_service
from backend.app.core.database import SessionLocal
from backend.app.main import app
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
)

client = TestClient(app)


@pytest.fixture
def cleanup_sync_test_data():
    yield
    db = SessionLocal()
    try:
        submissions = db.query(Submission).filter(Submission.application_reference.like("SYNC-%")).all()
        submission_ids = [item.id for item in submissions]
        if not submission_ids:
            return
        documents = db.query(Document).filter(Document.submission_id.in_(submission_ids)).all()
        document_ids = [item.id for item in documents]
        document_paths = [item.file_path for item in documents]
        renewals = db.query(Renewal).filter(
            (Renewal.predecessor_submission_id.in_(submission_ids))
            | (Renewal.successor_submission_id.in_(submission_ids))
        ).all()
        releases = db.query(ReleaseRequest).filter(ReleaseRequest.submission_id.in_(submission_ids)).all()
        discrepancies = db.query(Discrepancy).filter(Discrepancy.submission_id.in_(submission_ids)).all()
        verifications = db.query(BankVerification).filter(BankVerification.submission_id.in_(submission_ids)).all()
        confirmations = db.query(ManualConfirmation).filter(ManualConfirmation.submission_id.in_(submission_ids)).all()
        related_ids = submission_ids + document_ids + [item.id for item in renewals + releases + discrepancies + verifications + confirmations]
        db.query(AuditLog).filter(AuditLog.entity_id.in_(related_ids)).delete(synchronize_session=False)
        if document_ids:
            db.query(OCRResult).filter(OCRResult.document_id.in_(document_ids)).delete(synchronize_session=False)
        db.query(Notification).filter(Notification.submission_id.in_(submission_ids)).delete(synchronize_session=False)
        db.query(ReleaseRequest).filter(ReleaseRequest.submission_id.in_(submission_ids)).delete(synchronize_session=False)
        db.query(Renewal).filter(
            (Renewal.predecessor_submission_id.in_(submission_ids))
            | (Renewal.successor_submission_id.in_(submission_ids))
        ).delete(synchronize_session=False)
        db.query(Discrepancy).filter(Discrepancy.submission_id.in_(submission_ids)).delete(synchronize_session=False)
        db.query(BankVerification).filter(BankVerification.submission_id.in_(submission_ids)).delete(synchronize_session=False)
        db.query(ManualConfirmation).filter(ManualConfirmation.submission_id.in_(submission_ids)).delete(synchronize_session=False)
        db.query(Document).filter(Document.submission_id.in_(submission_ids)).delete(synchronize_session=False)
        db.query(Submission).filter(Submission.id.in_(submission_ids)).delete(synchronize_session=False)
        db.commit()
        for document_path in document_paths:
            Path(document_path).unlink(missing_ok=True)
    finally:
        db.close()


def create_accepted_submission(maturity_date="2027-01-24", application_reference=None):
    submission_id = f"TEST-{uuid.uuid4().hex[:10].upper()}"
    db = SessionLocal()
    try:
        db.add(Submission(
            id=submission_id,
            institution_id="INST-001",
            scenario="WORKFLOW_TEST",
            application_reference=application_reference or submission_id,
            instrument_type="FDR",
            entered_bank_id="DEMO-BANK-01",
            entered_fdr_number=f"TEST-FDR-{uuid.uuid4().hex[:8].upper()}",
            entered_depositor_name="Synthetic institution",
            entered_principal_amount="1000000.00",
            entered_currency="INR",
            entered_issue_date="2026-01-01",
            entered_maturity_date=maturity_date,
            entered_instrument_status="ACTIVE",
            entered_beneficiary_name="AICTE (demo only)",
            entered_lien_status="MARKED",
            entered_lien_in_favour_of="AICTE (demo only)",
            review_status="ACCEPTED",
            verification_status="CONFIRMED",
            submitted_at=clock_service.now_iso(),
            assigned_officer_id="USER-O01",
        ))
        db.commit()
    finally:
        db.close()
    return submission_id


def test_release_requires_all_three_authorized_steps_and_sanitizes_csv():
    submission_id = create_accepted_submission(application_reference="=HYPERLINK(\"https://example.invalid\")")
    college = {"X-Demo-User-Id": "USER-C01"}
    officer = {"X-Demo-User-Id": "USER-O01"}
    authority = {"X-Demo-User-Id": "USER-A01"}

    response = client.post(
        f"/api/submissions/{submission_id}/release-requests",
        json={"request_type": "RELEASE", "reason": "Institution reports zero liabilities."},
        headers=college,
    )
    assert response.status_code == 200
    release_id = response.json()["id"]
    for headers in (college, officer, authority):
        release_list = client.get("/api/release-requests", headers=headers)
        assert release_list.status_code == 200
        assert any(item["id"] == release_id for item in release_list.json())

    premature = client.post(
        f"/api/release-requests/{release_id}/execute",
        json={"discharge_reference": "DIS-001", "evidence": "Bank discharge received."},
        headers=officer,
    )
    assert premature.status_code == 409

    unauthorized_decision = client.post(
        f"/api/release-requests/{release_id}/decision",
        json={"decision": "APPROVED", "reason": "Approved."},
        headers=officer,
    )
    assert unauthorized_decision.status_code == 403

    recommended = client.post(
        f"/api/release-requests/{release_id}/recommend",
        json={"recommendation": "Zero liabilities checked; recommend release.", "zero_liabilities_verified": True},
        headers=officer,
    )
    assert recommended.status_code == 200
    for headers in (college, officer, authority):
        release_list = client.get("/api/release-requests", headers=headers)
        assert next(item for item in release_list.json() if item["id"] == release_id)["status"] == "RECOMMENDED"
    decision = client.post(
        f"/api/release-requests/{release_id}/decision",
        json={"decision": "APPROVED", "reason": "Approved by competent authority."},
        headers=authority,
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "APPROVED_EXECUTION_PENDING"
    for headers in (college, officer, authority):
        release_list = client.get("/api/release-requests", headers=headers)
        assert next(item for item in release_list.json() if item["id"] == release_id)["status"] == "APPROVED_EXECUTION_PENDING"

    executed = client.post(
        f"/api/release-requests/{release_id}/execute",
        json={"discharge_reference": "BANK-DISCHARGE-001", "evidence": "Formal discharge confirmed."},
        headers=officer,
    )
    assert executed.status_code == 200
    assert executed.json()["status"] == "COMPLETED"
    db = SessionLocal()
    try:
        released_submission = db.query(Submission).filter(Submission.id == submission_id).first()
        assert released_submission.entered_instrument_status == "RELEASED"
    finally:
        db.close()
    duplicate_release = client.post(
        f"/api/submissions/{submission_id}/release-requests",
        json={"request_type": "RELEASE", "reason": "Attempt to release twice."},
        headers=college,
    )
    assert duplicate_release.status_code == 409

    export = client.get("/api/reports/export.csv", headers=college)
    assert export.status_code == 200
    assert "'=HYPERLINK" in export.text
    report = client.get("/api/reports", headers=college)
    record = next(row for row in report.json()["items"] if row["submission_id"] == submission_id)
    assert record["release_status"] == "COMPLETED"
    assert record["instrument_status"] == "RELEASED"
    for headers in (officer, authority):
        report = client.get("/api/reports", headers=headers)
        record = next(row for row in report.json()["items"] if row["submission_id"] == submission_id)
        assert record["release_status"] == "COMPLETED"
        assert record["instrument_status"] == "RELEASED"
    officer_audit = client.get("/api/audit", headers=officer)
    assert officer_audit.status_code == 200
    assert any(item["entity_id"] == release_id and item["action"] == "RELEASE_REQUESTED" for item in officer_audit.json())
    for headers in (college, officer, authority):
        release_list = client.get("/api/release-requests", headers=headers)
        assert next(item for item in release_list.json() if item["id"] == release_id)["status"] == "COMPLETED"


def test_officer_review_rejection_and_audit_are_authorized_and_traceable():
    submission_id = create_accepted_submission(application_reference="REVIEW-ACTION-TEST")
    db = SessionLocal()
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        submission.review_status = "SUBMITTED"
        db.commit()
    finally:
        db.close()

    college = {"X-Demo-User-Id": "USER-C01"}
    officer = {"X-Demo-User-Id": "USER-O01"}
    assert client.post(f"/api/submissions/{submission_id}/start-review", headers=college).status_code == 403
    started = client.post(f"/api/submissions/{submission_id}/start-review", headers=officer)
    assert started.status_code == 200
    assert started.json()["review_status"] == "UNDER_REVIEW"

    rejected = client.post(
        f"/api/submissions/{submission_id}/reject",
        json={"reason": "Required supporting details were not provided."},
        headers=officer,
    )
    assert rejected.status_code == 200
    assert rejected.json()["review_status"] == "REJECTED"

    audit = client.get("/api/audit", headers=college)
    actions = [item["action"] for item in audit.json() if item["entity_id"] == submission_id]
    assert "SUBMISSION_REVIEW_STARTED" in actions
    assert "SUBMISSION_REJECTED_BY_OFFICER" in actions
    assert "SUBMISSION_DRAFT_CREATED" not in actions


def test_college_submission_and_renewal_changes_sync_across_portal_views(cleanup_sync_test_data):
    college = {"X-Demo-User-Id": "USER-C01"}
    officer = {"X-Demo-User-Id": "USER-O01"}
    authority = {"X-Demo-User-Id": "USER-A01"}
    roles = (college, officer, authority)
    unique = uuid.uuid4().hex[:8].upper()
    created = client.post(
        "/api/submissions",
        json={
            "application_reference": f"SYNC-{unique}",
            "bank_id": "DEMO-BANK-01",
            "fdr_number": f"SYNC-FDR-{unique}",
            "depositor_name": "Synthetic institution",
            "principal_amount": "1200000.00",
            "currency": "INR",
            "issue_date": "2026-01-15",
            "maturity_date": "2027-04-24",
        },
        headers=college,
    )
    assert created.status_code == 200
    submission_id = created.json()["id"]

    fixture_path = Path("fixtures/DOC-001.png")
    with fixture_path.open("rb") as document_file:
        uploaded = client.post(
            f"/api/submissions/{submission_id}/documents",
            files={"file": (fixture_path.name, io.BytesIO(document_file.read()), "image/png")},
            data={"doc_type": "FDR_RECEIPT"},
            headers=college,
        )
    assert uploaded.status_code == 200
    ocr_results = client.get(
        f"/api/documents/{uploaded.json()['id']}/ocr",
        headers=college,
    )
    assert ocr_results.status_code == 200
    corrected = client.put(
        f"/api/ocr-results/{ocr_results.json()[0]['id']}/correct",
        json={"corrected_value": "Reviewed value", "reason": "College visual review"},
        headers=college,
    )
    assert corrected.status_code == 200

    finalized = client.post(f"/api/submissions/{submission_id}/submit", headers=college)
    assert finalized.status_code == 200
    for headers in roles:
        submissions = client.get("/api/submissions", headers=headers)
        assert submissions.status_code == 200
        record = next(item for item in submissions.json() if item["id"] == submission_id)
        assert record["review_status"] == "SUBMITTED"
        report = client.get("/api/reports", headers=headers)
        assert next(item for item in report.json()["items"] if item["submission_id"] == submission_id)["review_status"] == "SUBMITTED"

    officer_audit = client.get("/api/audit", headers=officer)
    assert officer_audit.status_code == 200
    officer_ocr = client.get(f"/api/documents/{uploaded.json()['id']}/ocr", headers=officer)
    assert officer_ocr.status_code == 200
    assert any(item["corrected_value"] == "Reviewed value" for item in officer_ocr.json())
    submission_actions = {
        item["action"]
        for item in officer_audit.json()
        if item["entity_id"] == submission_id
    }
    assert "SUBMISSION_DRAFT_CREATED" in submission_actions
    assert "SUBMISSION_FINALIZED_AND_FROZEN" in submission_actions
    assert any(
        item["entity_id"] == corrected.json()["id"] and item["action"] == "OCR_FIELD_CORRECTED"
        for item in officer_audit.json()
    )

    started = client.post(f"/api/submissions/{submission_id}/start-review", headers=officer)
    assert started.status_code == 200
    for headers in roles:
        report = client.get("/api/reports", headers=headers)
        assert next(item for item in report.json()["items"] if item["submission_id"] == submission_id)["review_status"] == "UNDER_REVIEW"

    predecessor_id = create_accepted_submission(application_reference=f"SYNC-RENEWAL-{unique}")
    linked = client.post(
        f"/api/submissions/{predecessor_id}/renewal",
        json={
            "application_reference": f"SYNC-SUCCESSOR-{unique}",
            "bank_id": "DEMO-BANK-01",
            "fdr_number": f"SYNC-SUCCESSOR-FDR-{unique}",
            "depositor_name": "Synthetic institution",
            "principal_amount": "1200000.00",
            "currency": "INR",
            "issue_date": "2026-10-26",
            "maturity_date": "2027-10-26",
        },
        headers=college,
    )
    assert linked.status_code == 200
    renewal_id = linked.json()["renewal_id"]
    successor_id = linked.json()["successor"]
    for headers in roles:
        renewals = client.get("/api/renewals", headers=headers)
        renewal = next(item for item in renewals.json() if item["id"] == renewal_id)
        assert renewal["status"] == "PENDING"
        reports = client.get("/api/reports", headers=headers)
        successor = next(item for item in reports.json()["items"] if item["submission_id"] == successor_id)
        assert successor["renewal_status"] == "PENDING"

    successor_document = client.post(
        f"/api/submissions/{successor_id}/documents",
        files={"file": ("DOC-001.png", io.BytesIO(fixture_path.read_bytes()), "image/png")},
        data={"doc_type": "FDR_RECEIPT"},
        headers=college,
    )
    assert successor_document.status_code == 200
    assert client.post(f"/api/submissions/{successor_id}/submit", headers=college).status_code == 200
    db = SessionLocal()
    try:
        successor = db.query(Submission).filter(Submission.id == successor_id).first()
        successor.verification_status = "CONFIRMED"
        db.commit()
    finally:
        db.close()
    accepted = client.post(f"/api/submissions/{successor_id}/accept", headers=officer)
    assert accepted.status_code == 200
    for headers in roles:
        renewals = client.get("/api/renewals", headers=headers)
        assert next(item for item in renewals.json() if item["id"] == renewal_id)["status"] == "ACCEPTED"
        reports = client.get("/api/reports", headers=headers)
        rows = {item["submission_id"]: item for item in reports.json()["items"]}
        assert rows[successor_id]["review_status"] == "ACCEPTED"
        assert rows[successor_id]["verification_status"] == "CONFIRMED"
        assert rows[successor_id]["renewal_status"] == "ACCEPTED"
        assert rows[predecessor_id]["instrument_status"] == "SUPERSEDED"
    officer_audit = client.get("/api/audit", headers=officer)
    assert any(item["entity_id"] == renewal_id and item["action"] == "SUCCESSOR_DRAFT_LINKED" for item in officer_audit.json())
    assert any(item["entity_id"] == renewal_id and item["action"] == "SUCCESSOR_ACCEPTED_PREDECESSOR_SUPERSEDED" for item in officer_audit.json())


def test_renewal_supersedes_predecessor_only_after_successor_acceptance():
    predecessor_id = create_accepted_submission(maturity_date="2027-04-24")
    body = {
        "application_reference": f"{predecessor_id}-RENEWAL",
        "instrument_type": "FDR",
        "bank_id": "DEMO-BANK-01",
        "fdr_number": f"SUCCESSOR-{uuid.uuid4().hex[:8]}",
        "depositor_name": "Synthetic institution",
        "principal_amount": "1000000.00",
        "currency": "INR",
        "issue_date": "2026-10-26",
        "maturity_date": "2027-10-26",
    }
    linked = client.post(
        f"/api/submissions/{predecessor_id}/renewal",
        json=body,
        headers={"X-Demo-User-Id": "USER-C01"},
    )
    assert linked.status_code == 200
    successor_id = linked.json()["successor"]

    db = SessionLocal()
    try:
        predecessor = db.query(Submission).filter(Submission.id == predecessor_id).first()
        successor = db.query(Submission).filter(Submission.id == successor_id).first()
        renewal = db.query(Renewal).filter(Renewal.successor_submission_id == successor_id).first()
        assert predecessor.entered_instrument_status == "ACTIVE"
        assert renewal.status == "PENDING"
        successor.verification_status = "CONFIRMED"
        successor.review_status = "SUBMITTED"
        db.add(Document(
            id=f"TEST-DOC-{uuid.uuid4().hex[:8].upper()}",
            submission_id=successor_id,
            filename="successor.pdf",
            file_path="storage_private/successor.pdf",
            mime_type="application/pdf",
            sha256="0" * 64,
            file_size=1,
            uploaded_at=clock_service.now_iso(),
        ))
        db.commit()
    finally:
        db.close()

    accepted = client.post(f"/api/submissions/{successor_id}/accept", headers={"X-Demo-User-Id": "USER-O01"})
    assert accepted.status_code == 200
    db = SessionLocal()
    try:
        predecessor = db.query(Submission).filter(Submission.id == predecessor_id).first()
        renewal = db.query(Renewal).filter(Renewal.successor_submission_id == successor_id).first()
        assert predecessor.entered_instrument_status == "SUPERSEDED"
        assert renewal.status == "ACCEPTED"
    finally:
        db.close()


def test_reminder_job_is_idempotent():
    submission_id = create_accepted_submission(maturity_date="2027-01-24")
    headers = {"X-Demo-User-Id": "USER-O01"}
    first = client.post("/api/reminders/run", headers=headers)
    assert first.status_code == 200
    second = client.post("/api/reminders/run", headers=headers)
    assert second.status_code == 200
    assert second.json()["created"] == 0

    db = SessionLocal()
    try:
        count = db.query(Notification).filter(Notification.submission_id == submission_id).count()
        assert count == len((90, 60, 30, 7, 1, 0, -1, -7))
    finally:
        db.close()


def test_reminder_job_notifies_officer_of_pending_review():
    submission_id = create_accepted_submission(maturity_date="2027-01-24")
    db = SessionLocal()
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        submission.review_status = "UNDER_REVIEW"
        db.commit()
    finally:
        db.close()

    response = client.post("/api/reminders/run", headers={"X-Demo-User-Id": "USER-O01"})
    assert response.status_code == 200
    notifications = client.get("/api/notifications", headers={"X-Demo-User-Id": "USER-O01"})
    assert any(
        item["submission_id"] == submission_id
        and item["deadline_type"] == "PENDING_REVIEW"
        for item in notifications.json()
    )
