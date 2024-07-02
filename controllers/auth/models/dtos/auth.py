from pydantic import BaseModel


class AuthDTO(BaseModel):
    login: str
    password: str