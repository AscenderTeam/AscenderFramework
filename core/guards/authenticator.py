from typing import Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2AuthorizationCodeBearer
from core.extensions.authentication import AscenderAuthenticationFramework

class GetAuthenticatedUser:  
        def __init__(self, http_exception: bool = False) -> None:
            self.http_exception = http_exception
            if AscenderAuthenticationFramework.auth_provider is None:
                # TODO: Add custom exception
                raise Exception("Authentication provider is not initialized")
        
        async def __call__(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Any:
            provider = AscenderAuthenticationFramework.auth_provider

            user = await provider.get_authenticated_user(token)

            if self.http_exception and not user:
                raise HTTPException(status_code=401, detail="Unauthorized")

            return user


class IsAuthenticated:

    def __init__(self, is_superuser: bool = False) -> None:
        self.is_superuser = is_superuser
        if AscenderAuthenticationFramework.auth_provider is None:
            # TODO: Add custom exception
            raise Exception("Authentication provider is not initialized")
    
    async def has_permission(self, token: str) -> bool:
        provider = AscenderAuthenticationFramework.auth_provider

        user = await provider.get_authenticated_user(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        if self.is_superuser and not user.is_superuser:
            return False
    
    async def __call__(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Any:
        if await self.has_permission(token):
            return True
        else:
            raise HTTPException(status_code=404, detail="Not found")