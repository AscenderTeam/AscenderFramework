from pydantic import BaseModel, EmailStr, SecretStr


class UserDTO(BaseModel):
    username: str
    email: EmailStr
    password: str