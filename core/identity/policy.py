from typing import Any, Callable

from pydantic import BaseModel
from core.extensions.repositories import IdentityRepository
from core.identity.engine import IdentityEngine
from core.identity.handler import PolicyHandler
from core.identity.handlers.claims import ClaimHandler
from core.identity.handlers.roles import RoleHandler
from core.identity.types.claim_requirement import AppropriateValues, ClaimRequirement
from core.identity.types.role_requirement import RoleRequirement


class Policy:
    def __init__(self, engine: IdentityEngine, 
                 id_repo: IdentityRepository) -> None:
        self.engine = engine
        self._id_repo = id_repo
    
    def require_role(self, roles: str | list[str], error_code: int = 403):
        if isinstance(roles, str):
            roles = [roles]
        
        return RoleHandler(self.engine, self._id_repo, RoleRequirement(roles=roles, error_code=error_code))

    def require_claim(self, claim: str, value: AppropriateValues | list[AppropriateValues],
                      error_code: int = 403):
        return ClaimHandler(self.engine, self._id_repo, ClaimRequirement(
            claim=claim,
            value=value,
            error_code=error_code
        ))

    def require_custom(self, handler: type[PolicyHandler], requirement: BaseModel):
        return handler(self.engine, self._id_repo, requirement)