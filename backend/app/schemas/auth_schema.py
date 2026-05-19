from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    plan: str
    scan_count: int

    class Config:
        from_attributes = True