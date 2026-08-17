from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.common import APIResponse
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.models.invite_code import AdminInviteCode

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "viewer"
    invite_code: Optional[str] = None


@router.post("/register", response_model=APIResponse[Token])
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    role = (payload.role or "viewer").lower()

    # Admin registration requires a valid invite code
    if role == "admin":
        if not payload.invite_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An admin invite code is required to register as an administrator.",
            )
        invite = db.query(AdminInviteCode).filter(
            AdminInviteCode.code == payload.invite_code.strip(),
            AdminInviteCode.used == False,
        ).first()
        if not invite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or already-used invite code.",
            )
        if invite.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invite code has expired. Ask your administrator for a new one.",
            )

    user_in = UserCreate(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=role if role in ("admin", "manager", "viewer") else "viewer",
    )
    user = UserService.create(db, user_in)

    # Mark invite code as used
    if role == "admin":
        invite.used = True
        invite.used_by_id = user.id
        db.add(invite)
        db.commit()

    access_token = create_access_token(subject=user.id, role=user.role)
    token_data = Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
    return APIResponse(
        success=True,
        message="Registration successful",
        data=token_data
    )


@router.post("/login", response_model=APIResponse[Token])
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = UserService.get_by_email(db, user_in.email)
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Try again."
        )

    access_token = create_access_token(subject=user.id, role=user.role)
    token_data = Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
    return APIResponse(
        success=True,
        message="Login successful",
        data=token_data
    )


@router.post("/logout", response_model=APIResponse[dict])
def logout(current_user: User = Depends(get_current_user)):
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data={"user_id": current_user.id}
    )


@router.get("/me", response_model=APIResponse[UserResponse])
def get_me(current_user: User = Depends(get_current_user)):
    return APIResponse(
        success=True,
        message="User profile retrieved",
        data=UserResponse.model_validate(current_user)
    )
