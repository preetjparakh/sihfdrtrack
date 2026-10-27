import json
import hashlib
from pathlib import Path
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.models.models import (
    Institution, Bank, User, Submission, Document,
    BankVerification, ReleaseRequest, AuditLog
)

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def seed_database():
    Base.metadata.create_all(bind=engine)
    root = Path(__file__).resolve().parent.parent
    seed_path = root / "seed.json"
    data = json.loads(seed_path.read_text(encoding="utf-8"))

    db = SessionLocal()
    try:
        # Clear existing tables in reverse dependency order
        from backend.app.models.models import OCRResult, Discrepancy, ManualConfirmation, Notification, Renewal
        for model in [AuditLog, ReleaseRequest, BankVerification, ManualConfirmation, Discrepancy, Notification, Renewal, OCRResult, Document, Submission, User, Bank, Institution]:
            db.query(model).delete()
        db.commit()

        # 1. Institutions (10)
        for inst_data in data.get("institutions", []):
            db.add(Institution(
                id=inst_data["id"],
                name=inst_data["name"],
                region=inst_data["region"],
                email=inst_data["email"],
                representative_user_id=inst_data["representative_user_id"]
            ))
        db.commit()

        # 2. Banks (6)
        for b in data.get("banks", []):
            db.add(Bank(
                id=b["id"],
                name=b["name"],
                branch=b["branch"],
                verification_endpoint=b["verification_endpoint"],
                environment=b.get("environment", "MOCK")
            ))
        db.commit()

        # 3. Users (12)
        for u in data.get("users", []):
            db.add(User(
                id=u["id"],
                email=u["email"],
                role=u["role"],
                institution_id=u.get("institution_id")
            ))
        db.commit()

        # 4. Submissions (30)
        for s in data.get("submissions", []):
            fields = s.get("entered_fields", {})
            sub = Submission(
                id=s["id"],
                institution_id=s["institution_id"],
                scenario=s["scenario"],
                application_reference=s["application_reference"],
                instrument_type=s.get("instrument_type", "FDR"),
                entered_bank_id=fields.get("bank_id"),
                entered_fdr_number=fields.get("fdr_number", ""),
                entered_depositor_name=fields.get("depositor_name", ""),
                entered_principal_amount=str(fields.get("principal_amount", "0.00")),
                entered_currency=fields.get("currency", "INR"),
                entered_issue_date=str(fields.get("issue_date", "")),
                entered_maturity_date=str(fields.get("maturity_date", "")),
                entered_instrument_status=fields.get("instrument_status", "ACTIVE"),
                entered_beneficiary_name=fields.get("beneficiary_name"),
                entered_lien_status=fields.get("lien_status"),
                entered_lien_in_favour_of=fields.get("lien_in_favour_of"),
                entered_status_as_of=fields.get("status_as_of"),
                entered_record_updated_at=fields.get("record_updated_at"),
                review_status=s.get("review_status", "SUBMITTED"),
                verification_status=s.get("verification_status", "NOT_INITIATED"),
                submitted_at=s["submitted_at"],
                assigned_officer_id=s.get("assigned_officer_id"),
                renewal_due_date=str(s["renewal_due_date"]) if s.get("renewal_due_date") else None,
                document_valid_until=str(s["document_valid_until"]) if s.get("document_valid_until") else None,
                predecessor_submission_id=s.get("predecessor_submission_id"),
                required_document_types_json=json.dumps(s.get("required_document_types", [])),
                demo_renewal_required=bool(s.get("demo_renewal_required", False))
            )
            db.add(sub)
        db.commit()

        # 5. Documents (29) with real computed SHA256 and byte sizes
        for d in data.get("documents", []):
            png_file = root / "fixtures" / f"{d['id']}.png"
            sha256_hash = compute_sha256(png_file) if png_file.exists() else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            file_size = png_file.stat().st_size if png_file.exists() else 0
            doc = Document(
                id=d["id"],
                submission_id=d["submission_id"],
                doc_type=d.get("type", "FDR_RECEIPT"),
                layout_id=d.get("layout_id"),
                variant=d.get("variant", "standard"),
                filename=f"{d['id']}.png",
                file_path=str(png_file.relative_to(root)),
                mime_type="image/png",
                sha256=sha256_hash,
                file_size=file_size,
                uploaded_at=d.get("uploaded_at", "2026-10-26T03:30:00Z"),
                watermark=d.get("watermark", "SYNTHETIC - FOR PROTOTYPE ONLY"),
                ground_truth_json=json.dumps(d.get("ground_truth", {})),
                expected_ocr_review=d.get("expected_ocr_review")
            )
            db.add(doc)
        db.commit()

        # 6. Historical Verifications (2)
        for v in data.get("verification_history", []):
            ver = BankVerification(
                id=v["id"],
                submission_id=v["submission_id"],
                verification_id=f"HIST-{v['id']}",
                bank_id="DEMO-BANK-01",
                fdr_number="FDR-2026-HIST",
                method=v.get("method", "SIMULATED_BANK_API"),
                environment=v.get("environment", "MOCK"),
                lookup_status=v.get("status", "CONFIRMED"),
                requested_at=v["requested_at"],
                responded_at=v["responded_at"],
                status_as_of="2026-10-26T04:00:00Z",
                confirmed_fields_json=json.dumps(v.get("confirmed_fields", {})),
                unsupported_fields_json="[]",
                source_reference=v.get("source_reference", "CBS-HIST"),
                evidence_note=v.get("evidence_note"),
                recorded_by=v.get("recorded_by")
            )
            db.add(ver)
        db.commit()

        # 7. Release Requests (3)
        for r in data.get("release_requests", []):
            rel = ReleaseRequest(
                id=r["id"],
                submission_id=r["submission_id"],
                request_type=r.get("request_type", "RELEASE"),
                reason=r.get("reason", "Matured security deposit refund"),
                status=r.get("status", "REQUESTED"),
                requested_at=r["requested_at"],
                approved_by=r.get("approved_by"),
                approved_at=r.get("approved_at"),
                executed_at=r.get("executed_at"),
                execution_reference=r.get("execution_reference")
            )
            db.add(rel)
        db.commit()

        # 8. Audit Events (30)
        for a in data.get("audit_events", []):
            audit = AuditLog(
                id=a["id"],
                entity_type="submission",
                entity_id=a["submission_id"],
                actor_id=a["actor_id"],
                action=a["action"],
                timestamp=a["at"],
                source_reference=a.get("environment", "MOCK")
            )
            db.add(audit)
        db.commit()

        print("Successfully seeded AICTE FDR Portal database:")
        print(f"  Institutions: {db.query(Institution).count()}")
        print(f"  Banks: {db.query(Bank).count()}")
        print(f"  Users: {db.query(User).count()}")
        print(f"  Submissions: {db.query(Submission).count()}")
        print(f"  Documents: {db.query(Document).count()} (with computed SHA-256 hashes)")
        print(f"  Historical Verifications: {db.query(BankVerification).count()}")
        print(f"  Release Requests: {db.query(ReleaseRequest).count()}")
        print(f"  Audit Events: {db.query(AuditLog).count()}")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
