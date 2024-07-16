from typing import Self

from pydantic import BaseModel
from core.extensions.repositories import IdentityRepository
from core.identity.engine import IdentityEngine


class PolicyHandler:
    _repository: IdentityRepository
    
    def __init__(self, engine: IdentityEngine, _repository: IdentityRepository,
                 requirement: BaseModel) -> None:
        self._repository = _repository
        self._engine = engine
        self._requirement = requirement
    
    def __call__(self):
        pass
