from functools import wraps
from typing import Any, Callable

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from core.identity.errors.uninitialized import UninitializedSecurity
from core.identity.manager import IdentityManager
from core.identity.singleton import SecuritySingleton
from core.identity.types.claim_requirement import AppropriateValues
from core.registries.service import ServiceRegistry
from settings import AUTHORIZATION_SCHEME


class AuthRefresher:
    def __init__(self, parameter_name: str = "credentials") -> None:
        self.parameter_name = parameter_name
        self.registry = ServiceRegistry()
    
    def extract_handler(self, refresh_token: HTTPAuthorizationCredentials = Security(AUTHORIZATION_SCHEME)):
        identity_manager = self.registry.get_singletone(IdentityManager)

        if not identity_manager:
            raise UninitializedSecurity()
        
        credentials = identity_manager.reauthorize(token=refresh_token.credentials)

        if not credentials:
            raise HTTPException(401, "Incorrect refresh token")
        
        return credentials[0], credentials[1]

    def __call__(self, executable: Callable[..., Any]) -> Any:
        # warn: Changing function's metadata
        from inspect import signature, Parameter

        sig = signature(executable)
        new_parameters = []

        for name, param in sig.parameters.items():
            if name == self.parameter_name and param.default == Parameter.empty:
                new_parameters.append(
                    Parameter(name, param.kind, default=Depends(self.extract_handler)))
            else:
                new_parameters.append(param)

        if not len(new_parameters):
            # TODO: Make a specific exception for this case
            raise ValueError(
                f"Parameter {self.parameter_name} was not specified in controller's endpoint function")

        new_sig = sig.replace(parameters=new_parameters)
        executable.__signature__ = new_sig

        @wraps(executable)
        async def wrapper(*args, **kwargs):
            return await executable(*args, **kwargs)

        return wrapper