from datetime import datetime
from pydantic import BaseModel, SecretStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserDTO(BaseModel):
    username: str
    password: SecretStr
    email: str

class LoginDTO(BaseModel):
    username: str
    password: SecretStr