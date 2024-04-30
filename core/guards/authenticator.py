from typing import Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.errors.authentication import UninitializedAuthprovider
from core.extensions.authentication import AscenderAuthenticationFramework
from core.utils.sockets import ApplicationContext


class GetAuthenticatedUser:
    def __init__(self, http_exception: bool = False) -> None:
        self.http_exception = http_exception
        if AscenderAuthenticationFramework.auth_provider is None:
            # TODO: Add custom exception
            raise Exception("Authentication provider is not initialized")

    async def __call__(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Any:
        provider = AscenderAuthenticationFramework.auth_provider
        user = await provider.get_authenticated_user(token.credentials)

        if self.http_exception and not user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        return user


class IsAuthenticated:

    def __init__(self, is_superuser: bool = False) -> None:
        self.is_superuser = is_superuser
        if AscenderAuthenticationFramework.auth_provider is None:
            raise UninitializedAuthprovider()

    async def has_permission(self, token: str) -> bool:
        provider = AscenderAuthenticationFramework.auth_provider

        user = await provider.get_authenticated_user(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if self.is_superuser and not user.is_superuser:
            return False
        
        return True

    async def __call__(self, token: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> Any:
        if await self.has_permission(token.credentials):
            return True
        else:
            raise HTTPException(status_code=403, detail="Permission denied")


class IsAuthenticatedSocket:
    def __init__(self, is_superuser: bool = False) -> None:
        """
        ## Is Authenticated Socket

        This is used to check on @Listen('connect') if the user is authenticated or not.
        """
        self.is_superuser = is_superuser
        if AscenderAuthenticationFramework.auth_provider is None:
            raise UninitializedAuthprovider()

    async def has_permission(self, token: str) -> bool:
        provider = AscenderAuthenticationFramework.auth_provider

        user = await provider.get_authenticated_user(token)
        if user is None:
            return False

        if self.is_superuser and not user.is_superuser:
            return False

        return True

    def __call__(self, f) -> Any:
        
        async def inner_wrapper(controller: object, ctx: ApplicationContext, *args):
            if ctx.event == "connect":
                token: str = ctx.environ.get("HTTP_AUTHORIZATION", "").removeprefix("Bearer ")
                
                if await self.has_permission(token):
                    await ctx.save_session({"token": token})
                    return await f(controller, ctx, *args)

                await ctx.answer("error", {"message": "Unauthorized"})
                await ctx.disconnect()
                return False

            session = await ctx.get_session()
            if await self.has_permission(session.get("token", None)):
                return await f(controller, ctx, *args)
            else:
                await ctx.disconnect()
        
        return inner_wrapper

class GetAuthenticatedSocket:
    def __init__(self, disconnect_on_error: bool = False) -> None:
        self.disconnect_on_error = disconnect_on_error

    def __call__(self, f) -> Any:
        
        provider = AscenderAuthenticationFramework.auth_provider
        
        async def inner_wrapper(controller: object, ctx: ApplicationContext):
            if ctx.event == "connect":
                token: str = ctx.environ.get("HTTP_AUTHORIZATION", "").removeprefix("Bearer ")
                user = await provider.get_authenticated_user(token)
                if user:
                    await ctx.save_session({"token": token})
                    return await f(controller, ctx, user)
                
                if self.disconnect_on_error:
                    await ctx.answer("error", {"message": "Unauthorized"})
                    await ctx.disconnect()
                    return
                
                return await f(controller, ctx, None)

            session = await ctx.get_session()
            user = await provider.get_authenticated_user(session.get("token", None))
            if user:
                return await f(controller, ctx, user)
            else:
                if self.disconnect_on_error:
                    await ctx.disconnect()
                    return
                
                return await f(controller, ctx, None)
        
        return inner_wrapper