from datetime import datetime, timedelta
import uuid
from core.extensions.authentication.entity import SessionEntity, UserEntity


class SessionManager:
    
    async def create_session(self, user: UserEntity, life_time: timedelta) -> SessionEntity:
        # Generate token: Generates UUID4 token for session
        _token = self._generate_token(user.id, datetime.now().timestamp())
        
        entity = SessionEntity(user=user, token=_token, expires_at=datetime.now() + life_time)
        await entity.save()

        return entity
    
    async def get_session(self, token: str) -> SessionEntity | None:
        query = await SessionEntity.filter(token=token).prefetch_related('user').first()

        return query
    
    async def delete_session(self, token: str) -> None:
        await SessionEntity.filter(token=token).delete()

    def _generate_token(self, starting_integer: int, timestamp: float) -> str:
        # Make API token generator custom, that not only uses UUID4, but also uses user id and timestamp
        # to make token more unique and secure
        return f"asc-{starting_integer}{uuid.uuid4()}-{timestamp}"