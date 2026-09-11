from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# -------------------------
# Request Models
# -------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# Register User
# -------------------------

@router.post("/register")
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    # Hash the password
    hashed_password = pwd_context.hash(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "message": "User registered successfully",
    }


# -------------------------
# Login User
# -------------------------

@router.post("/login")
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):

    # Find user
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    # Check email
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    # Check password
    if not pwd_context.verify(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    return {
        "id": user.id,
        "email": user.email,
        "message": "Login successful",
    }