import json
from pathlib import Path
from mock_bank.app.database import engine, Base, SessionLocal
from mock_bank.app.models import MockBankRecord

def seed_mock_bank():
    Base.metadata.create_all(bind=engine)
    root = Path(__file__).resolve().parent.parent
    seed_path = root / "seed.json"
    data = json.loads(seed_path.read_text(encoding="utf-8"))

    db = SessionLocal()
    try:
        if db.query(MockBankRecord).first():
            print("Mock bank records already exist; keeping existing records.")
            return
        db.query(MockBankRecord).delete()
        records = []
        for r in data.get("bank_records", []):
            rec = MockBankRecord(
                bank_id=r["bank_id"],
                fdr_number=r["fdr_number"],
                depositor_name=r["depositor_name"],
                principal_amount=str(r["principal_amount"]),
                currency=r.get("currency", "INR"),
                issue_date=str(r["issue_date"]),
                maturity_date=str(r["maturity_date"]),
                instrument_status=r.get("instrument_status", "ACTIVE"),
                beneficiary_name=r.get("beneficiary_name"),
                lien_status=r.get("lien_status"),
                lien_in_favour_of=r.get("lien_in_favour_of"),
                status_as_of=r["status_as_of"],
                record_updated_at=r["record_updated_at"]
            )
            records.append(rec)
        db.bulk_save_objects(records)
        db.commit()
        print(f"Successfully seeded {len(records)} authoritative mock bank records into mock_bank.db!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_mock_bank()
