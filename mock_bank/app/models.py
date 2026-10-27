from sqlalchemy import Column, String, PrimaryKeyConstraint
from mock_bank.app.database import Base

class MockBankRecord(Base):
    __tablename__ = "mock_bank_records"

    bank_id = Column(String(50), nullable=False)
    fdr_number = Column(String(100), nullable=False)
    depositor_name = Column(String(255), nullable=False)
    principal_amount = Column(String(50), nullable=False)
    currency = Column(String(10), default="INR")
    issue_date = Column(String(20), nullable=False)
    maturity_date = Column(String(20), nullable=False)
    instrument_status = Column(String(50), default="ACTIVE")
    beneficiary_name = Column(String(255), nullable=True)
    lien_status = Column(String(50), nullable=True)
    lien_in_favour_of = Column(String(255), nullable=True)
    status_as_of = Column(String(50), nullable=False)
    record_updated_at = Column(String(50), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("bank_id", "fdr_number"),
    )
