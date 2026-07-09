from pydantic import BaseModel, EmailStr
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "worker"
    pay_model: str = "A"
    hourly_rate: float = 0.0
    commission_rate: float = 0.0
    bonus_rate: float = 0.0

class EmployeeCreate(EmployeeBase):
    password: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    pay_model: Optional[str] = None
    hourly_rate: Optional[float] = None
    commission_rate: Optional[float] = None
    bonus_rate: Optional[float] = None

class EmployeeResponse(EmployeeBase):
    id: int
    
    class Config:
        from_attributes = True