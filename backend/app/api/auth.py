from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import create_access_token
from backend.app.api.deps import get_current_user
from backend.app.models.models import User, Institution
from backend.app.schemas.schemas import UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

COLLEGE_DISPLAY_NAMES = {
    "USER-C01": "Aarav Sharma",
    "USER-C02": "Ananya Iyer",
    "USER-C03": "Rohan Deshmukh",
    "USER-C04": "Priya Patel",
    "USER-C05": "Vikram Sengupta",
    "USER-C06": "Kavya Nair",
    "USER-C07": "Aditya Agarwal",
    "USER-C08": "Meera Mehta",
}

class LoginRequest(BaseModel):
    user_id: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PersonaItem(BaseModel):
    id: str
    email: str
    role: str
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None
    badge: str

@router.get("/personas", response_model=List[PersonaItem])
def list_demo_personas(db: Session = Depends(get_db)):
    """
    Returns the available demonstration personas for the profile switcher.
    """
    users = db.query(User).all()
    institutions = {inst.id: inst.name for inst in db.query(Institution).all()}
    personas = []
    for u in users:
        inst_name = institutions.get(u.institution_id) if u.institution_id else None
        if u.role == "COLLEGE":
            display_name = COLLEGE_DISPLAY_NAMES.get(u.id)
            badge = f"{display_name} · College Representative" if display_name else f"College Rep ({inst_name or u.institution_id})"
        elif u.role == "OFFICER":
            badge = "AICTE Scrutiny Officer"
        else:
            badge = "AICTE Competent Authority"
        personas.append(PersonaItem(
            id=u.id,
            email=u.email,
            role=u.role,
            institution_id=u.institution_id,
            institution_name=inst_name,
            badge=badge
        ))
    return personas

@router.post("/token", response_model=TokenResponse)
def login_for_access_token(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {payload.user_id} not found in provisioned fixtures."
        )
    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "institution_id": user.institution_id
    })
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
