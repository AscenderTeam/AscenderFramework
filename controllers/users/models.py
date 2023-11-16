from typing import Optional
from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool

class UserDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_active: bool

class GithubUserResponse(BaseModel):
    id: int
    login: str
    label: Optional[str] = None

class GithubUserDTO(BaseModel):
    login: str
    access_token: str
    label: Optional[str] = None