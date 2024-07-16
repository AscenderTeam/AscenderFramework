from datetime import timedelta
from typing import Any
from fastapi.security import HTTPBasic


class IdentityBasicScheme:
    def __init__(self, secret: str, expires: timedelta | None = None) -> None:
        self.security = HTTPBasic()

        from jwt import encode, decode
        self.encoder = encode
        self.decoder = decode

        self.secret = secret
        self.expires = expires

    def decode_token(self, token: str) -> dict:
        return self.decoder(token, self.secret, ["HS256"])

    def generate_token(self, user_id: str, 
                       roles: list[str] = [],
                       claims: dict[str, Any] = {}) -> str:
        token = self.encoder({"data": {"user_id": user_id,  
                                       "roles": roles,
                                       "claims": claims}, "exp": self.expires},
                             self.secret)

        return token
