from entities.user import UserEntity
from sqlalchemy import func
from ascender.common import Injectable
from ascender.contrib.repositories import Repository


@Injectable()
class AppRepo(Repository):
    
    async def create_user(self, **data) -> UserEntity:
        async with self._context() as _db:
            entity = UserEntity(**data)
            
            _db.add(entity)
            await _db.commit()
            await _db.refresh(entity)
        
        return entity

    async def update_user(self, user_id: int, **data) -> UserEntity:
        async with self._context() as _db:
            entity = await _db.get(UserEntity, user_id)
            
            for k, v in data.items():
                setattr(entity, k, v)
            
            await _db.commit()
            await _db.refresh(entity)
        
        return UserEntity

    async def get_users(self) -> list[UserEntity]:
        query = await self._context.construct(UserEntity)

        return query.scalars().all()

    async def get_users_offset(self, offset: int, limit: int) -> list[UserEntity]:
        query = await self._context.construct(UserEntity).offset(offset).limit(limit)

        return query.scalars().all()

    async def get_users_count(self) -> int:
        query = self._context.construct(UserEntity).subquery()
        count = await self._context.construct(func.count).select_from(query)

        return count.scalar()

    async def get_user(self, user_id: int) -> UserEntity | None:
        query = await self._context.construct(UserEntity).filter(UserEntity.id == user_id)

        return query.scalar()

    def fetch_user(self):
        return self._context.construct(UserEntity)
