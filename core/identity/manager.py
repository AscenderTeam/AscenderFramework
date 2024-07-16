from typing import Any
from core.identity.engine import IdentityEngine


class IdentityManager:
    def __init__(self, engine: IdentityEngine) -> None:
        self.engine = engine
    
    def authorize(self, user_id: int, roles: list[str],
                  claims: dict[str, Any]):
        _credentials = self.engine.authenticate(user_id, roles, claims)

        if isinstance(_credentials, tuple):
            return _credentials[0], _credentials[1]
        
        return _credentials
    
    def reauthorize(self, token: str):
        return self.engine.refresh_credentials(token)