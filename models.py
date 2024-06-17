from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone: str
    company_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    email: EmailStr
    phone: str
    company_name: str

class InternalUserResponse(UserResponse):
    password: bytes

class SessionCreate(BaseModel):
    session_name: str

class SessionResponse(BaseModel):
    id: int
    session_name: str
    user_email: EmailStr

class UserWithSessionsResponse(UserResponse):
    sessions: List[SessionResponse]
