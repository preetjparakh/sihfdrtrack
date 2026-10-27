import os
import uuid
import hashlib
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from backend.app.core.config import settings

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

def get_storage_base() -> Path:
    base = Path(settings.STORAGE_DIR).resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base

def sanitize_filename(filename: str) -> str:
    cleaned = "".join(c for c in filename if c.isalnum() or c in (".", "-", "_")).strip()
    return cleaned or "document.bin"

def save_uploaded_file(file: UploadFile, submission_id: str) -> Tuple[str, str, int, str]:
    """
    Saves an uploaded file to private storage.
    Returns (relative_file_path, sha256_hash, file_size_bytes, mime_type).
    """
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    expected_mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".pdf": "application/pdf",
    }[ext]
    if file.content_type not in (expected_mime, "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content type does not match a supported document format.",
        )

    base = get_storage_base()
    sub_dir = base / submission_id
    sub_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(file.filename or f"doc{ext}")
    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    target_path = sub_dir / unique_name

    hasher = hashlib.sha256()
    file_size = 0

    with open(target_path, "wb") as f:
        while chunk := file.file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE_BYTES:
                f.close()
                target_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
                )
            hasher.update(chunk)
            f.write(chunk)

    with open(target_path, "rb") as f:
        signature = f.read(8)
    valid_signature = (
        (expected_mime == "image/png" and signature.startswith(b"\x89PNG\r\n\x1a\n"))
        or (expected_mime == "image/jpeg" and signature.startswith(b"\xff\xd8\xff"))
        or (expected_mime == "application/pdf" and signature.startswith(b"%PDF-"))
    )
    if not valid_signature:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded bytes do not match the declared document format.",
        )

    sha256 = hasher.hexdigest()
    mime = expected_mime

    # Relative path from project root for portability
    rel_path = str(target_path.relative_to(Path.cwd())).replace("\\", "/")
    return rel_path, sha256, file_size, mime
