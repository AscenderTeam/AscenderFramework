from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from core.extensions.repositories import IdentityRepository
from core.identity.engine import IdentityEngine
from core.identity.handler import PolicyHandler
from core.identity.types.role_requirement import RoleRequirement
from settings import AUTHORIZATION_SCHEME


class RoleHandler(PolicyHandler):
    _requirement: RoleRequirement

    def __init__(self, engine: IdentityEngine, _repository: IdentityRepository, requirement: RoleRequirement) -> None:
        super().__init__(engine, _repository, requirement)
    
    async def __call__(self, token: HTTPAuthorizationCredentials = Security(AUTHORIZATION_SCHEME)):
        try:
            roles = self._engine.extract_identity(token.credentials)["roles"]
        except Exception as e:
            raise HTTPException(401)

        for role in self._requirement:
            if role not in roles:
                raise HTTPException(self._requirement.error_code)