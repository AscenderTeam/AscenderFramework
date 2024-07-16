from typing import Any, Callable, Literal, Self
from core.database.engine import DatabaseEngine
from core.database.orms.sqlalchemy import SQLAlchemyORM
from core.extensions.repositories import IdentityRepository
from core.identity.engine import IdentityEngine
from core.identity.handler import PolicyHandler
from core.identity.handlers.claims import ClaimHandler
from core.identity.handlers.roles import RoleHandler
from core.identity.policy import Policy
from threading import Lock

from core.identity.types.claim_requirement import ClaimRequirement
from core.identity.types.role_requirement import RoleRequirement
from core.registries.service import ServiceRegistry


class Security:

    def __init__(self, identity_repository: IdentityRepository,
                 auth_scheme: Literal["basic", "apikey", "oauth2", "cookie"] = "basic",
                 *scheme_args, **scheme_kargs) -> None:
        self.engine = IdentityEngine(auth_scheme=auth_scheme,
                                     *scheme_args, **scheme_kargs)
        self.service_registry = ServiceRegistry()

        # Defining IdentityRepository
        self.identity_repository = identity_repository
        
        # Incapsulated arguments
        self.__policies = {}
        self._lock = Lock()
    
    def add_policy(self, name: str, handler: Callable[[Policy], PolicyHandler]):
        with self._lock:
            policy = Policy(self.engine, self.identity_repository)
            self.__policies[name] = handler(policy)
    
    def get_policy(self, name: str) -> PolicyHandler:
        return self.__policies[name]
    
    def get_handler(self, handler_type: Literal["claims", "roles"], requirements: RoleRequirement | ClaimRequirement):
        if handler_type == "roles" and isinstance(requirements, RoleRequirement):
            return RoleHandler(self.engine, self.identity_repository, requirements)
        
        if handler_type == "claims" and isinstance(requirements, ClaimRequirement):
            return ClaimHandler(self.engine, self.identity_repository, requirements)
        
        raise ValueError("Handler type or requirements are incorrect. Handler type should be one of 'claims' or 'roles'")
    