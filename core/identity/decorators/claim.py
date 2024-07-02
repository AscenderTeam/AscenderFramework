from functools import wraps
from typing import Any, Callable
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from core.identity.singleton import SecuritySingleton
from settings import AUTHORIZATION_SCHEME
from jwt.exceptions import PyJWTError


class Claim:
    def __init__(self, parameter_name: str = "user_claim") -> None:
        self.parameter_name = parameter_name
        self.security = SecuritySingleton()

    def extract_handler(self, token: HTTPAuthorizationCredentials = Security(AUTHORIZATION_SCHEME)):
        try:
            claim = self.security.engine.extract_identity(token=token.credentials)
        except PyJWTError:
            return None
        
        return {
            "user_id": claim["user_id"],
            "claims": claim["claims"]
        }

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
