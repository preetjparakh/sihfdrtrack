from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from backend.app.core.config import settings
from backend.app.core.clock import clock_service
from backend.app.api.deps import require_officer_user
from backend.app.models.models import User
from backend.app.api import auth, submissions, documents, dashboard, verification, discrepancies, workflows

app = FastAPI(
    title="AICTE Security Deposit / FDR Management Portal",
    description="Centralized FDR / Security Deposit portal for AICTE Regulation Bureau and technical institutions.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(submissions.router)
app.include_router(documents.router)
app.include_router(dashboard.router)
app.include_router(verification.router)
app.include_router(discrepancies.router)
app.include_router(workflows.router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "aicte-fdr-portal",
        "env": settings.APP_ENV,
        "demo_clock": clock_service.now_iso(),
        "display_time": clock_service.now_display(),
        "synthetic_watermark": "SYNTHETIC - FOR PROTOTYPE ONLY"
    }

class AdvanceClockRequest(BaseModel):
    days: int = Field(default=0, ge=0, le=3650)
    hours: int = Field(default=0, ge=0, le=87600)
    minutes: int = Field(default=0, ge=0, le=5256000)

@app.get("/api/demo/clock")
def get_clock():
    return {
        "frozen_iso": clock_service.now_iso(),
        "display_ist": clock_service.now_display(),
        "is_frozen": clock_service._is_frozen,
        "today_local": str(clock_service.today_local_date())
    }

@app.post("/api/demo/clock/advance")
def advance_clock(payload: AdvanceClockRequest, current_user: User = Depends(require_officer_user)):
    if settings.APP_ENV != "demo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clock manipulation restricted to demo environment."
        )
    clock_service.advance_time(days=payload.days, hours=payload.hours, minutes=payload.minutes)
    return {
        "message": f"Clock advanced by {payload.days}d {payload.hours}h {payload.minutes}m",
        "new_clock_iso": clock_service.now_iso(),
        "display_ist": clock_service.now_display()
    }

@app.post("/api/demo/clock/reset")
def reset_clock(current_user: User = Depends(require_officer_user)):
    clock_service.reset_to_seed()
    return {
        "message": "Clock reset to initial seed demo time.",
        "clock_iso": clock_service.now_iso(),
        "display_ist": clock_service.now_display()
    }
