from pydantic import BaseModel, EmailStr
from typing import List, Optional

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
    file_path: Optional[str] = None
    vector_store_id: Optional[str] = None
    thread_id: Optional[str] = None

class UserWithSessionsResponse(UserResponse):
    sessions: List[SessionResponse]
