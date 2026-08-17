from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import APIResponse
from app.services.user_service import UserService
from app.core.deps import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.put("/me", response_model=APIResponse[UserResponse])
def update_my_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated = UserService.update_profile(db, current_user, user_in)
    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=UserResponse.model_validate(updated)
    )


@router.get("", response_model=APIResponse[List[UserResponse]])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = UserService.list_users(db, skip=skip, limit=limit)
    return APIResponse(
        success=True,
        message="Users list retrieved",
        data=[UserResponse.model_validate(u) for u in users]
    )
