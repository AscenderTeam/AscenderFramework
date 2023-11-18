
from datetime import datetime, timedelta
from core.extensions.authentication.entity import SessionEntity, UserEntity


class SessionManager:
    
    async def create_session(self, user: UserEntity, life_time: timedelta) -> SessionEntity:
        entity = SessionEntity(user=user, token="token", expires_at=datetime.now() + life_time)
        await entity.save()

        return entity
    
    async def get_session(self, token: str) -> SessionEntity | None:
        query = await SessionEntity.filter(token=token).prefetch_related('user').first()

        return query
    
    async def delete_session(self, token: str) -> None:
        await SessionEntity.filter(token=token).delete()