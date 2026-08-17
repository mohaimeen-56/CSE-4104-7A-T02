import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.common import APIResponse
from app.schemas.maintenance import (
    MaintenanceStatus, MaintenanceEnableRequest, MaintenanceDisableRequest, MaintenanceLogItem,
)
from app.services.maintenance_service import MaintenanceService
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.models.invite_code import AdminInviteCode

router = APIRouter(prefix="/admin", tags=["Admin"])

INVITE_CODE_TTL_HOURS = 48


class InviteCodeResponse(BaseModel):
    id: int
    code: str
    created_at: datetime
    expires_at: datetime
    used: bool
    used_by_name: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/maintenance", response_model=APIResponse[MaintenanceStatus])
def get_maintenance_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Any authenticated user may read maintenance status (the frontend needs this to
    decide whether to render the maintenance screen), but only admins can change it."""
    status = MaintenanceService.get_status(db)
    return APIResponse(success=True, message="Maintenance status retrieved", data=status)


@router.post("/maintenance/enable", response_model=APIResponse[MaintenanceStatus])
def enable_maintenance(
    payload: MaintenanceEnableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    status = MaintenanceService.enable(db, current_user, reason=payload.reason, message=payload.message)
    return APIResponse(success=True, message="Maintenance mode enabled", data=status)


@router.post("/maintenance/disable", response_model=APIResponse[MaintenanceStatus])
def disable_maintenance(
    payload: MaintenanceDisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    status = MaintenanceService.disable(db, current_user, reason=payload.reason)
    return APIResponse(success=True, message="Maintenance mode disabled", data=status)


@router.get("/maintenance/audit-log", response_model=APIResponse[List[MaintenanceLogItem]])
def get_maintenance_audit_log(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    logs = MaintenanceService.get_audit_log(db)
    return APIResponse(success=True, message="Maintenance audit log retrieved", data=logs)


# ── Admin Invite Codes ────────────────────────────────────────────────────────

@router.post("/invite-codes", response_model=APIResponse[InviteCodeResponse])
def generate_invite_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Generate a one-time admin invite code (valid for 48 hours)."""
    code = AdminInviteCode(
        code=uuid.uuid4().hex,
        created_by_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(hours=INVITE_CODE_TTL_HOURS),
    )
    db.add(code)
    db.commit()
    db.refresh(code)
    return APIResponse(
        success=True,
        message="Invite code generated. Share it securely — it expires in 48 hours and can only be used once.",
        data=InviteCodeResponse(
            id=code.id,
            code=code.code,
            created_at=code.created_at,
            expires_at=code.expires_at,
            used=code.used,
        ),
    )


@router.get("/invite-codes", response_model=APIResponse[List[InviteCodeResponse]])
def list_invite_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all invite codes created by this admin (active and used)."""
    codes = (
        db.query(AdminInviteCode)
        .filter(AdminInviteCode.created_by_id == current_user.id)
        .order_by(AdminInviteCode.created_at.desc())
        .limit(20)
        .all()
    )
    result = []
    for c in codes:
        result.append(InviteCodeResponse(
            id=c.id,
            code=c.code,
            created_at=c.created_at,
            expires_at=c.expires_at,
            used=c.used,
            used_by_name=c.used_by.name if c.used_by else None,
        ))
    return APIResponse(success=True, message="Invite codes retrieved", data=result)


@router.delete("/invite-codes/{code_id}", response_model=APIResponse[dict])
def revoke_invite_code(
    code_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Revoke (delete) an unused invite code."""
    code = db.query(AdminInviteCode).filter(
        AdminInviteCode.id == code_id,
        AdminInviteCode.created_by_id == current_user.id,
    ).first()
    if not code:
        raise HTTPException(status_code=404, detail="Invite code not found.")
    if code.used:
        raise HTTPException(status_code=400, detail="Cannot revoke a code that has already been used.")
    db.delete(code)
    db.commit()
    return APIResponse(success=True, message="Invite code revoked.", data={"id": code_id})
