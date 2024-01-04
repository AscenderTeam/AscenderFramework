from controllers.auth.models import UserDTO, UserResponse
from core.extensions.authentication import AscenderAuthenticationFramework
from core.extensions.serializer import Serializer
from core.extensions.services import Service
from controllers.auth.repository import AuthRepo


class AuthService(Service):

    def __init__(self, repository: AuthRepo) -> None:
        self._repository = repository
        self.auth_provider = AscenderAuthenticationFramework.auth_provider
    
    async def create_user(self, dto: UserDTO):
        user = await self.auth_provider.create_user(dto.username, dto.password.get_secret_value())
        
        user = await self._repository.update_user_from_entity(user, email=dto.email)
        response = Serializer(UserResponse, user)
        return response()
    
    async def delete_user(self, user_id: str):
        user = await self.auth_provider.get_user(user_id)
        if not user:
            return False
        
        return await self._repository.delete_user(user)