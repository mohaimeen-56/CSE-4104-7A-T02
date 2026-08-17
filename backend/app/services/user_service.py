from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email.ilike(email.strip())).first()

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).order_by(User.id.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user_in: UserCreate) -> User:
        existing = UserService.get_by_email(db, user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

        hashed_pw = get_password_hash(user_in.password)
        user = User(
            name=user_in.name.strip(),
            email=user_in.email.strip().lower(),
            password_hash=hashed_pw,
            role=user_in.role or "viewer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_profile(db: Session, user: User, user_in: UserUpdate) -> User:
        if user_in.name:
            user.name = user_in.name.strip()

        if user_in.password:
            if not user_in.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required to set a new password"
                )
            if not verify_password(user_in.current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            user.password_hash = get_password_hash(user_in.password)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user
