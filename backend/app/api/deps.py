from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.models import User

security_bearer = HTTPBearer(auto_error=False)

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    x_demo_user_id: Optional[str] = Header(None, alias="X-Demo-User-Id"),
    db: Session = Depends(get_db)
) -> User:
    user = None
    # 1. Bearer Token
    if auth and auth.credentials:
        payload = decode_access_token(auth.credentials)
        if payload and payload.sub:
            user = db.query(User).filter(User.id == payload.sub).first()

    # 2. Demo User ID Header (for prototype testing and demo persona switcher)
    if not user and x_demo_user_id:
        user = db.query(User).filter(User.id == x_demo_user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide valid Bearer token or X-Demo-User-Id header."
        )
    return user

def require_college_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "COLLEGE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="College representative permission required."
        )
    return user

def require_officer_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "OFFICER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AICTE Scrutiny Officer permission required."
        )
    return user

def require_approver_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "APPROVER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AICTE Competent Authority permission required."
        )
    return user

def verify_institution_access(target_institution_id: str, user: User):
    """
    Enforces strict cross-institution isolation:
    - AICTE Officers and Approvers can access any institution's submissions.
    - College representatives can ONLY access their own institution's submissions.
    """
    if user.role in ("OFFICER", "APPROVER"):
        return True
    if user.role == "COLLEGE" and user.institution_id == target_institution_id:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Access denied: User {user.id} ({user.institution_id}) cannot access records of institution {target_institution_id}."
    )
