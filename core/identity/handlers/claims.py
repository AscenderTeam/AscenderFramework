from typing import Any
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from core.extensions.repositories import IdentityRepository
from core.identity.engine import IdentityEngine
from core.identity.handler import PolicyHandler
from core.identity.types.claim_requirement import AppropriateValues, ClaimRequirement
from settings import AUTHORIZATION_SCHEME


class ClaimHandler(PolicyHandler):
    _requirement: ClaimRequirement

    def __init__(self, engine: IdentityEngine, _repository: IdentityRepository, requirement: ClaimRequirement) -> None:
        super().__init__(engine, _repository, requirement)
    
    def validate_claim(self, entity: Any, value: AppropriateValues):
        if not hasattr(entity, self._requirement.claim):
                raise HTTPException(self._requirement.error_code)
        return getattr(entity, self._requirement.claim) == value

    async def __call__(self, token: HTTPAuthorizationCredentials = Security(AUTHORIZATION_SCHEME)):
        try:
            user_id = self._engine.extract_identity(token.credentials)["user_id"]
        except:
            raise HTTPException(401)

        user = await self._repository.get_user(user_id)

        if not user:
            raise HTTPException(401)

        if not isinstance(self._requirement.value, list):
            if not self.validate_claim(user, self._requirement.value):
                raise HTTPException(self._requirement.error_code)
        
        for value in self._requirement.value:
            _validated = self.validate_claim(user, value)

            if not _validated:
                raise HTTPException(self._requirement.error_code)