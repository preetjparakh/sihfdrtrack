import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.orm import Session
from backend.app.core.clock import clock_service
from backend.app.models.models import AuditLog

def log_audit_event(
    db: Session,
    entity_type: str,
    entity_id: str,
    actor_id: str,
    action: str,
    before_state: Optional[Any] = None,
    after_state: Optional[Any] = None,
    reason: Optional[str] = None,
    source_reference: Optional[str] = None
) -> AuditLog:
    before_json = json.dumps(before_state) if before_state is not None else None
    after_json = json.dumps(after_state) if after_state is not None else None

    audit_entry = AuditLog(
        id=f"AUD-Z{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}-{uuid.uuid4().hex[:8].upper()}",
        entity_type=entity_type,
        entity_id=entity_id,
        actor_id=actor_id,
        action=action,
        timestamp=clock_service.now_iso(),
        before_state_json=before_json,
        after_state_json=after_json,
        reason=reason,
        source_reference=source_reference
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry
