from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    region = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    representative_user_id = Column(String(50), nullable=False)

    users = relationship("User", back_populates="institution")
    submissions = relationship("Submission", back_populates="institution")

class Bank(Base):
    __tablename__ = "banks"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    branch = Column(String(255), nullable=False)
    verification_endpoint = Column(String(255), nullable=False)
    environment = Column(String(20), default="MOCK")

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # COLLEGE, OFFICER, APPROVER
    institution_id = Column(String(50), ForeignKey("institutions.id"), nullable=True)

    institution = relationship("Institution", back_populates="users")

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(50), primary_key=True, index=True)
    institution_id = Column(String(50), ForeignKey("institutions.id"), nullable=False, index=True)
    scenario = Column(String(50), nullable=False)
    application_reference = Column(String(100), nullable=False, index=True)
    instrument_type = Column(String(50), default="FDR")

    # Entered fields
    entered_bank_id = Column(String(50), nullable=True)
    entered_fdr_number = Column(String(100), nullable=False, index=True)
    entered_depositor_name = Column(String(255), nullable=False)
    entered_principal_amount = Column(String(50), nullable=False)
    entered_currency = Column(String(10), default="INR")
    entered_issue_date = Column(String(20), nullable=False)
    entered_maturity_date = Column(String(20), nullable=False, index=True)
    entered_instrument_status = Column(String(50), default="ACTIVE")
    entered_beneficiary_name = Column(String(255), nullable=True)
    entered_lien_status = Column(String(50), nullable=True)
    entered_lien_in_favour_of = Column(String(255), nullable=True)
    entered_status_as_of = Column(String(50), nullable=True)
    entered_record_updated_at = Column(String(50), nullable=True)

    # Status dimensions
    review_status = Column(String(50), default="SUBMITTED", index=True)
    verification_status = Column(String(50), default="NOT_INITIATED", index=True)

    submitted_at = Column(String(50), nullable=False)
    assigned_officer_id = Column(String(50), ForeignKey("users.id"), nullable=True)
    renewal_due_date = Column(String(20), nullable=True, index=True)
    document_valid_until = Column(String(20), nullable=True)
    predecessor_submission_id = Column(String(50), nullable=True, index=True)
    required_document_types_json = Column(Text, default="[]")
    demo_renewal_required = Column(Boolean, default=False)

    institution = relationship("Institution", back_populates="submissions")
    documents = relationship("Document", back_populates="submission", cascade="all, delete-orphan")
    verifications = relationship("BankVerification", back_populates="submission", cascade="all, delete-orphan")
    discrepancies = relationship("Discrepancy", back_populates="submission", cascade="all, delete-orphan")
    release_requests = relationship("ReleaseRequest", back_populates="submission", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="submission", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True, index=True)
    submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    doc_type = Column(String(50), default="FDR_RECEIPT")
    layout_id = Column(String(20), nullable=True)
    variant = Column(String(50), default="standard")
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    mime_type = Column(String(50), default="image/png")
    sha256 = Column(String(64), nullable=False)
    file_size = Column(Integer, default=0)
    uploaded_at = Column(String(50), nullable=False)
    uploaded_by = Column(String(50), ForeignKey("users.id"), nullable=True)
    watermark = Column(String(100), default="SYNTHETIC - FOR PROTOTYPE ONLY")
    ground_truth_json = Column(Text, nullable=True)  # Evaluation ground truth ONLY
    expected_ocr_review = Column(String(50), nullable=True)

    submission = relationship("Submission", back_populates="documents")
    ocr_results = relationship("OCRResult", back_populates="document", cascade="all, delete-orphan")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(String(50), primary_key=True, index=True)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=False, index=True)
    engine_version = Column(String(50), nullable=False)
    processed_at = Column(String(50), nullable=False)
    raw_text = Column(Text, nullable=False)
    field = Column(String(50), nullable=False, index=True)
    raw_value = Column(String(500), nullable=False)
    normalized_value = Column(String(500), nullable=True)
    confidence = Column(Float, nullable=True)
    page = Column(Integer, default=1)
    bounding_box_json = Column(Text, nullable=True)
    review_status = Column(String(50), default="EXTRACTED")  # EXTRACTED, VERIFIED, CORRECTED
    corrected_value = Column(String(500), nullable=True)
    corrected_by = Column(String(50), ForeignKey("users.id"), nullable=True)
    corrected_at = Column(String(50), nullable=True)

    document = relationship("Document", back_populates="ocr_results")

class BankVerification(Base):
    __tablename__ = "bank_verifications"

    id = Column(String(50), primary_key=True, index=True)
    submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    verification_id = Column(String(100), nullable=False, index=True)
    bank_id = Column(String(50), nullable=False)
    fdr_number = Column(String(100), nullable=False)
    method = Column(String(50), default="SIMULATED_BANK_API")
    environment = Column(String(20), default="MOCK")
    lookup_status = Column(String(50), nullable=False)  # FOUND, NOT_FOUND, SOURCE_UNAVAILABLE, MANUAL_REQUIRED
    requested_at = Column(String(50), nullable=False)
    responded_at = Column(String(50), nullable=False)
    status_as_of = Column(String(50), nullable=True)
    confirmed_fields_json = Column(Text, default="{}")
    unsupported_fields_json = Column(Text, default="[]")
    source_reference = Column(String(100), nullable=False)
    evidence_note = Column(Text, nullable=True)
    recorded_by = Column(String(50), ForeignKey("users.id"), nullable=True)

    submission = relationship("Submission", back_populates="verifications")

class ManualConfirmation(Base):
    __tablename__ = "manual_confirmations"

    id = Column(String(50), primary_key=True, index=True)
    submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    officer_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    contact_source = Column(String(255), nullable=False)
    evidence_doc_id = Column(String(50), nullable=True)
    confirmed_fields_json = Column(Text, default="{}")
    confirmed_at = Column(String(50), nullable=False)
    notes = Column(Text, nullable=False)

class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id = Column(String(50), primary_key=True, index=True)
    submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    field = Column(String(50), nullable=False)
    submitted_value = Column(String(500), nullable=True)
    document_value = Column(String(500), nullable=True)
    source_value = Column(String(500), nullable=True)
    reason = Column(Text, nullable=False)
    evidence_document_id = Column(String(50), nullable=True)
    assigned_to = Column(String(50), default="COLLEGE")
    created_at = Column(String(50), nullable=False)
    response_due_date = Column(String(20), nullable=True)
    college_response = Column(Text, nullable=True)
    response_submitted_at = Column(String(50), nullable=True)
    resolved_by = Column(String(50), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(String(50), nullable=True)
    resolution = Column(String(50), nullable=True)

    submission = relationship("Submission", back_populates="discrepancies")

class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(String(50), primary_key=True, index=True)
    predecessor_submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    successor_submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    linked_at = Column(String(50), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, ACCEPTED, SUPERSEDED
    notes = Column(Text, nullable=True)

class ReleaseRequest(Base):
    __tablename__ = "release_requests"

    id = Column(String(50), primary_key=True, index=True)
    submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    request_type = Column(String(50), default="RELEASE")  # REFUND, DISCHARGE, RELEASE
    reason = Column(Text, nullable=False)
    status = Column(String(50), default="REQUESTED")  # REQUESTED, UNDER_REVIEW, RECOMMENDED, APPROVED_EXECUTION_PENDING, REJECTED, RETURNED, COMPLETED
    requested_at = Column(String(50), nullable=False)
    officer_recommendation = Column(Text, nullable=True)
    recommended_at = Column(String(50), nullable=True)
    recommended_by = Column(String(50), ForeignKey("users.id"), nullable=True)
    authority_decision = Column(String(50), nullable=True)  # APPROVED, REJECTED, RETURNED
    decision_reason = Column(Text, nullable=True)
    approved_by = Column(String(50), ForeignKey("users.id"), nullable=True)
    approved_at = Column(String(50), nullable=True)
    execution_reference = Column(String(100), nullable=True)
    execution_evidence = Column(Text, nullable=True)
    executed_by = Column(String(50), ForeignKey("users.id"), nullable=True)
    executed_at = Column(String(50), nullable=True)

    submission = relationship("Submission", back_populates="release_requests")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(50), primary_key=True, index=True)
    submission_id = Column(String(50), ForeignKey("submissions.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    deadline_type = Column(String(50), nullable=False)
    due_date = Column(String(20), nullable=False)
    offset_days = Column(Integer, nullable=False)
    recipient_user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    channel = Column(String(50), default="IN_APP")
    scheduled_at = Column(String(50), nullable=False)
    sent_at = Column(String(50), nullable=True)
    delivery_status = Column(String(50), default="SCHEDULED")
    dedupe_key = Column(String(255), unique=True, index=True, nullable=False)

    submission = relationship("Submission", back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(50), primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(50), nullable=False, index=True)
    actor_id = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    timestamp = Column(String(50), nullable=False, index=True)
    before_state_json = Column(Text, nullable=True)
    after_state_json = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    source_reference = Column(String(100), nullable=True)
