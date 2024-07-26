from pydantic import BaseModel, EmailStr, SecretStr, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: EmailStr
