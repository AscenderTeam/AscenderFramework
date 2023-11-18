from typing import TypeVar, Generic
from fastapi.security import OAuth2PasswordBearer

from core.extensions.authentication.sessions import SessionManager

T = TypeVar("T")
S = TypeVar("S", bound=SessionManager)

class AuthenticationProvider(Generic[T, S]):

    session: S
    oauth2_scheme: OAuth2PasswordBearer

    async def authenticate(self, login: str, password: str) -> str:
        raise NotImplementedError()
    
    async def get_authenticated_user(self, token: str) -> T | None:
        raise NotImplementedError()
    
    async def create_user(self, login: str, password: str) -> T:
        raise NotImplementedError()
    
    async def create_superuser(self, login: str, password: str) -> T:
        raise NotImplementedError()
    
    async def get_user(self, user_id: int) -> T | None:
        raise NotImplementedError()
    
    async def get_user_by_login(self, login: str) -> T | None:
        raise NotImplementedError()