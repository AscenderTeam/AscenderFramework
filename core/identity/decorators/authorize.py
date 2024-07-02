from functools import wraps
from typing import Any, Callable

from fastapi import Depends
from core.identity.singleton import SecuritySingleton
from core.identity.types.claim_requirement import AppropriateValues


class Authorize:
    def __init__(self, policy: str, 
                 role: str | None = None,
                 claims: dict[str, AppropriateValues | list[AppropriateValues]] | None = None) -> None:
        self.policy = policy
        self.role = role
        self.claims = claims
        self.security = SecuritySingleton()
    
    def extract_handler(self):
        try:
            policy = self.security.get_policy(self.policy)
        except KeyError:
            # TODO: Add an exception
            raise Exception
        
        return policy

    def __call__(self, executable: Callable[..., Any]) -> Any:
        handler = self.extract_handler()
        if not getattr(executable, "_dependencies", None):
            setattr(executable, "_dependencies", [Depends(handler)])
            return executable
        setattr(executable, "_dependencies", [*getattr(executable, "_dependencies"), Depends(handler)])
        getattr(executable, "_dependencies", [])

        @wraps(executable)
        async def wrapper(*args, **kwargs):
            return await executable(*args, **kwargs)

        return wrapper