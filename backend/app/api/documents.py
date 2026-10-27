import json
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.clock import clock_service
from backend.app.api.deps import get_current_user, verify_institution_access
from backend.app.models.models import User, Submission, Document, OCRResult
from backend.app.schemas.schemas import DocumentResponse, OCRResultResponse
from backend.app.services.storage import save_uploaded_file
from backend.app.services.mock_ocr import generate_mock_extraction
from backend.app.services.audit import log_audit_event

router = APIRouter(tags=["documents"])

class OCRCorrectionRequest(BaseModel):
    corrected_value: str
    reason: Optional[str] = "Manual verification correction by user"

@router.post("/api/submissions/{submission_id}/documents", response_model=DocumentResponse)
def upload_submission_document(
    submission_id: str,
    file: UploadFile = File(...),
    doc_type: str = Form("FDR_RECEIPT"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {submission_id} not found."
        )

    verify_institution_access(submission.institution_id, current_user)
    if current_user.role != "COLLEGE" or submission.review_status != "DRAFT":
        raise HTTPException(
            status_code=403,
            detail="Only the institution representative can upload documents to a draft submission.",
        )

    rel_path, sha256_hash, file_size, mime = save_uploaded_file(file, submission_id)
    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"

    doc = Document(
        id=doc_id,
        submission_id=submission_id,
        doc_type=doc_type,
        layout_id="custom",
        variant="uploaded",
        filename=file.filename or f"{doc_id}.bin",
        file_path=rel_path,
        mime_type=mime,
        sha256=sha256_hash,
        file_size=file_size,
        uploaded_at=clock_service.now_iso(),
        uploaded_by=current_user.id,
        watermark="SYNTHETIC - FOR PROTOTYPE ONLY",
        expected_ocr_review=None
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    extracted_fields, raw_text = generate_mock_extraction(f"{sha256_hash}:{doc.id}")
    for field in extracted_fields:
        db.add(OCRResult(
            id=f"OCR-{uuid.uuid4().hex[:10].upper()}",
            document_id=doc.id,
            engine_version="mock-data-generator-1.0",
            processed_at=clock_service.now_iso(),
            raw_text=raw_text,
            field=field["field"],
            raw_value=field["raw_value"],
            normalized_value=field["normalized_value"],
            confidence=field["confidence"],
            page=field["page"],
            bounding_box_json=json.dumps(field["bounding_box"]),
            review_status=field["review_status"],
        ))
    db.commit()

    log_audit_event(
        db=db,
        entity_type="document",
        entity_id=doc.id,
        actor_id=current_user.id,
        action="DOCUMENT_UPLOADED_AND_MOCK_EXTRACTION_GENERATED",
        after_state={
            "filename": doc.filename,
            "sha256": sha256_hash,
            "size": file_size,
            "extraction_mode": "MOCK_DATA_ONLY",
        },
        source_reference="USER_UPLOAD"
    )

    return DocumentResponse.model_validate(doc)

@router.get("/api/documents/{document_id}/file")
def get_document_file(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    sub = db.query(Submission).filter(Submission.id == doc.submission_id).first()
    if sub:
        verify_institution_access(sub.institution_id, current_user)

    file_path = Path(doc.file_path).resolve()
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file missing on disk.")

    return FileResponse(path=file_path, media_type=doc.mime_type, filename=doc.filename)

@router.get("/api/documents/{document_id}/ocr", response_model=List[OCRResultResponse])
def get_document_ocr_results(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    sub = db.query(Submission).filter(Submission.id == doc.submission_id).first()
    if sub:
        verify_institution_access(sub.institution_id, current_user)

    ocr_results = db.query(OCRResult).filter(OCRResult.document_id == document_id).all()
    return [OCRResultResponse.model_validate(r) for r in ocr_results]

@router.put("/api/ocr-results/{result_id}/correct", response_model=OCRResultResponse)
def correct_ocr_field(
    result_id: str,
    payload: OCRCorrectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ocr_res = db.query(OCRResult).filter(OCRResult.id == result_id).first()
    if not ocr_res:
        raise HTTPException(status_code=404, detail="OCR result record not found.")

    doc = db.query(Document).filter(Document.id == ocr_res.document_id).first()
    if doc:
        sub = db.query(Submission).filter(Submission.id == doc.submission_id).first()
        if sub:
            verify_institution_access(sub.institution_id, current_user)
            if current_user.role != "COLLEGE" or sub.review_status != "DRAFT":
                raise HTTPException(
                    status_code=403,
                    detail="OCR corrections are limited to the institution representative during draft review.",
                )

    before_val = ocr_res.corrected_value or ocr_res.normalized_value or ocr_res.raw_value
    ocr_res.corrected_value = payload.corrected_value
    ocr_res.corrected_by = current_user.id
    ocr_res.corrected_at = clock_service.now_iso()
    ocr_res.review_status = "CORRECTED"
    db.commit()
    db.refresh(ocr_res)

    log_audit_event(
        db=db,
        entity_type="ocr_result",
        entity_id=ocr_res.id,
        actor_id=current_user.id,
        action="OCR_FIELD_CORRECTED",
        before_state={"field": ocr_res.field, "value": before_val},
        after_state={"field": ocr_res.field, "value": payload.corrected_value},
        reason=payload.reason
    )

    return OCRResultResponse.model_validate(ocr_res)
