from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core.security import decode_token
from app.database.connection import get_db
from app.database.models import Employee
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    role: str = payload.get("role")
    
    if email is None:
        raise credentials_exception
    
    token_data = TokenData(email=email, role=role)
    
    # Get user from database
    user = db.query(Employee).filter(Employee.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: Employee = Depends(get_current_user)
):
    """Get current active user"""
    return current_user

def require_role(required_role: str):
    """Dependency to require a specific role"""
    async def role_checker(
        current_user: Employee = Depends(get_current_user)
    ):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. {required_role} role required."
            )
        return current_user
    return role_checker