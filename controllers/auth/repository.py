from pydantic import EmailStr
from sqlalchemy import or_
from core.database.dbcontext import AppDBContext
from core.extensions.authentication.password_manager import AuthPassManager
from entities.user import UserEntity
from core.extensions.repositories import IdentityRepository, Repository


class AuthRepo(IdentityRepository):
    def __init__(self, _context: AppDBContext) -> None:
        self._context = _context
    
    async def create_user(self, username: str, email: EmailStr, password: str) -> UserEntity:
        async with self._context() as db:
            entity = UserEntity(username=username, email=email.lower(), password=password)
            db.add(entity)
            await db.commit()
            await db.refresh(entity)
        
        return entity

    async def update_user(self, user_id: int, **new_values) -> UserEntity | None:
        async with self._context() as db:
            entity = await db.get(UserEntity, user_id)
            
            if not entity:
                return None
            
            for key, value in new_values.items():
                setattr(entity, key, value)

        return entity
    
    async def get_user(self, user_id: int) -> UserEntity | None:
        query = await self._context.construct(UserEntity).filter(UserEntity.id == user_id)

        result = query.first()
        return result[0] if result else None
    
    async def get_user_by_login(self, login: str) -> UserEntity | None:
        query = await self._context.construct(UserEntity).filter(
            or_(UserEntity.username == login, UserEntity.email == login.lower()))
        result = query.first()
        return result[0] if result else None
    
    async def delete_user(self, user_id: int) -> None:
        async with self._context() as db:
            entity = await db.get(UserEntity, user_id)
            if not entity:
                return None
                
            await db.delete(entity)