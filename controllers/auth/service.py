from fastapi import HTTPException
from controllers.auth.models import AuthDTO, UserDTO, UserResponse
from core.extensions.authentication.password_manager import AuthPassManager
from core.extensions.services import Service
from controllers.auth.repository import AuthRepo
from core.identity.manager import IdentityManager


class AuthService(Service):

    _identity: IdentityManager

    def __init__(self, repository: AuthRepo) -> None:
        self._repository = repository
    
    async def create_user(self, data: UserDTO):
        # Hash the password
        data.password = AuthPassManager.hash_password(data.password)

        # Create the user using _repository
        user = await self._repository.create_user(data.username, data.email,
                                                  data.password)
        # Return newly created user
        return UserResponse.model_validate(user)

    async def authenticate(self, data: AuthDTO):
        # Get the user by login
        user = await self._repository.get_user_by_login(data.login)

        if not user:
            raise HTTPException(401, "Not authenticated")

        # Check the password
        _passcheck = AuthPassManager.check_password(data.password, user.password)

        if not _passcheck:
            raise HTTPException(401, "Not authenticated")
        
        # Apply Authorization and Policies to user
        identity_credentials = self._identity.authorize(user.id, ["user"], {
            "username": user.username,
            "email": user.email
        })

        if isinstance(identity_credentials, tuple):
            return {"access_token": identity_credentials[0], 
                    "refresh_token": identity_credentials[1],
                    "type": "bearer"}

        return {"access_token": identity_credentials, "type": "basic"}
    
    async def get_user(self, user_id: int):
        user = await self._repository.get_user(user_id)

        return UserResponse.model_validate(user)