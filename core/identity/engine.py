from typing import Any, Literal
from core.identity import schemas
from core.identity.errors.incorrectscheme import IncorrectSchemeError


class IdentityEngine:
    def __init__(self, auth_scheme: Literal["basic", "apikey", "oauth2", "cookie"] = "basic",
                 *scheme_args, **scheme_kargs) -> None:
        self.auth_scheme = auth_scheme
        self.auth_scheme_processor = schemas.get_scheme(
            auth_scheme, *scheme_args, **scheme_kargs)

    def authenticate(self, user_id: int,
                           roles: list[str] = [],
                           claims: dict[str, Any] = {}):
        match self.auth_scheme:
            case "basic":
                access_token = self.auth_scheme_processor.generate_token(user_id,
                                                                         roles=roles,
                                                                         claims=claims)
                return access_token

            case "oauth2":
                access_token, refresh_token = self.auth_scheme_processor.generate_token(user_id,
                                                                                        roles=roles,
                                                                                        claims=claims)
                return access_token, refresh_token

            case _:
                return None
            
    def refresh_credentials(self, refresh_token: str):
        if self.auth_scheme != "oauth2":
            raise IncorrectSchemeError()
        
        return self.auth_scheme_processor.refresh_token(refresh_token)
    
    def has_role(self, token: str, role: str):
        try:
            data = self.auth_scheme_processor.decode_token(token)["data"]
        except Exception:
            return False
        
        if role not in data["roles"]:
            return False
        
        return True
    
    def extract_identity(self, token: str):
        data = self.auth_scheme_processor.decode_token(token)["data"]

        return data