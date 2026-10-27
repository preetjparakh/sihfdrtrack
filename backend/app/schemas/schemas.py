from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    institution_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class InstitutionResponse(BaseModel):
    id: str
    name: str
    region: str
    email: str
    representative_user_id: str
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: str
    submission_id: str
    doc_type: str
    layout_id: Optional[str] = None
    variant: str
    filename: str
    file_path: str
    mime_type: str
    sha256: str
    file_size: int
    uploaded_at: str
    watermark: str
    expected_ocr_review: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class OCRResultResponse(BaseModel):
    id: str
    document_id: str
    engine_version: str
    processed_at: str
    field: str
    raw_value: str
    normalized_value: Optional[str] = None
    confidence: Optional[float] = None
    page: int
    bounding_box_json: Optional[str] = None
    review_status: str
    corrected_value: Optional[str] = None
    corrected_by: Optional[str] = None
    corrected_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SubmissionResponse(BaseModel):
    id: str
    institution_id: str
    scenario: str
    application_reference: str
    instrument_type: str
    entered_bank_id: Optional[str] = None
    entered_fdr_number: str
    entered_depositor_name: str
    entered_principal_amount: str
    entered_currency: str
    entered_issue_date: str
    entered_maturity_date: str
    entered_instrument_status: str
    entered_beneficiary_name: Optional[str] = None
    entered_lien_status: Optional[str] = None
    entered_lien_in_favour_of: Optional[str] = None
    review_status: str
    verification_status: str
    submitted_at: str
    assigned_officer_id: Optional[str] = None
    renewal_due_date: Optional[str] = None
    document_valid_until: Optional[str] = None
    predecessor_submission_id: Optional[str] = None
    demo_renewal_required: bool
    model_config = ConfigDict(from_attributes=True)

class DiscrepancyResponse(BaseModel):
    id: str
    submission_id: str
    field: str
    submitted_value: Optional[str] = None
    document_value: Optional[str] = None
    source_value: Optional[str] = None
    reason: str
    evidence_document_id: Optional[str] = None
    assigned_to: str
    created_at: str
    response_due_date: Optional[str] = None
    college_response: Optional[str] = None
    response_submitted_at: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None
    resolution: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class BankVerificationResponse(BaseModel):
    id: str
    verification_id: str
    bank_id: str
    fdr_number: str
    lookup_status: str
    requested_at: str
    responded_at: str
    confirmed_fields_json: str
    unsupported_fields_json: str
    source_reference: str
    evidence_note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ReleaseRequestSummaryResponse(BaseModel):
    id: str
    request_type: str
    reason: str
    status: str
    requested_at: str
    officer_recommendation: Optional[str] = None
    authority_decision: Optional[str] = None
    decision_reason: Optional[str] = None
    execution_reference: Optional[str] = None
    executed_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SubmissionDetailResponse(SubmissionResponse):
    institution: Optional[InstitutionResponse] = None
    documents: List[DocumentResponse] = []
    ocr_results: List[OCRResultResponse] = []
    discrepancies: List[DiscrepancyResponse] = []
    verifications: List[BankVerificationResponse] = []
    release_requests: List[ReleaseRequestSummaryResponse] = []

class AuditLogResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    actor_id: str
    action: str
    timestamp: str
    before_state_json: Optional[str] = None
    after_state_json: Optional[str] = None
    reason: Optional[str] = None
    source_reference: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DashboardStatsResponse(BaseModel):
    demo_clock: str
    display_time: str
    total_submissions: int
    pending_review: int
    under_review: int
    pending_bank_confirmation: int
    confirmed_submissions: int
    mismatched_submissions: int
    active_discrepancies: int
    approaching_maturity: int
    matured: int
    pending_renewals: int
    pending_releases: int
