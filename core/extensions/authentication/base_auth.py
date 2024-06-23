from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError
from core.errors.authentication import AlreadyExistsError, IncorrectPasswordError, UserNotFoundError
from core.extensions.authentication.custom.provider import AuthenticationProvider
from core.extensions.authentication.entity import UserEntity
from core.extensions.authentication.password_manager import AuthPassManager
from core.extensions.authentication.sessions import SessionManager
from datetime import datetime, timedelta


class BaseAuthentication(AuthenticationProvider[UserEntity, SessionManager]):

    def __init__(self, token_url: str) -> None:
        self.sessions = SessionManager()
        self.oauth2_scheme = OAuth2PasswordBearer(token_url)

    async def authenticate(self, login: str, password: str) -> str:
        login = login.strip()
        password = password.strip()

        user = await self.get_user_by_login(login)
        if not user:
            raise UserNotFoundError(login)
        
        if not AuthPassManager.check_password(password, user.password):
            raise IncorrectPasswordError(login)
        
        session = self.sessions.create_session(user, timedelta(days=1))

        return session
    
    async def get_authenticated_user(self, token: str) -> UserEntity | None:
        try:
            session = self.sessions.get_session(token)
        except ExpiredSignatureError:
            return None
        
        except InvalidTokenError:
            return None
        # Fix: https://github.com/AscenderTeam/AscenderFramework/issues/13
        try:
            user = await UserEntity.filter(id=session.get("user")).first()
            if not user:
                return None
        except Exception:
            # Fix: https://github.com/AscenderTeam/AscenderFramework/issues/13
            return None
        
        return user
    
    async def create_user(self, login: str, password: str) -> UserEntity:
        login = login.strip()
        password = password.strip()

        user = await self.get_user_by_login(login)
        if user:
            raise AlreadyExistsError(login)
        
        hashed_password = AuthPassManager.hash_password(password)
        user = await UserEntity.create(username=login, password=hashed_password)
        return user
    
    async def create_superuser(self, login: str, password: str) -> UserEntity:
        login = login.strip()
        password = password.strip()

        user = await self.get_user_by_login(login)
        if user:
            raise AlreadyExistsError(login)
        
        hashed_password = AuthPassManager.hash_password(password)
        user = await UserEntity.create(username=login, password=hashed_password, is_superuser=True)
        return user
    
    async def get_user(self, user_id: int) -> UserEntity | None:
        query = await UserEntity.filter(id=user_id).first()

        return query
    
    async def get_user_by_login(self, login: str) -> UserEntity | None:
        query = await UserEntity.filter(username=login).first()

        return query