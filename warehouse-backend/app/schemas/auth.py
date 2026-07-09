from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "worker"
    pay_model: str = "A"
    hourly_rate: float = 0.0
    commission_rate: float = 0.0
    bonus_rate: float = 0.0

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str
    role: str