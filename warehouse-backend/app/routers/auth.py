from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_user
from app.database.connection import get_db
from app.database.models import Employee
from app.schemas.auth import UserCreate, Token
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=None)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:  # ← IMPORTANT: Use -> Any
    """Register a new user"""
    existing_user = db.query(Employee).filter(Employee.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = Employee(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        pay_model=user_data.pay_model,
        hourly_rate=user_data.hourly_rate,
        commission_rate=user_data.commission_rate,
        bonus_rate=user_data.bonus_rate
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email
    }

@router.post("/login", response_model=None)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:  # ← IMPORTANT: Use -> Any
    """Login to get access token"""
    user = db.query(Employee).filter(Employee.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(
    current_user: Employee = Depends(get_current_user)
) -> Any:  # ← IMPORTANT: Use -> Any
    """Get current user info"""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "pay_model": current_user.pay_model
    }

