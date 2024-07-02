from datetime import datetime, timedelta
from typing import Any
from fastapi.security import OAuth2PasswordBearer


class IdentityOAuth2Scheme:
    def __init__(self, secret: str, *,
                 token_url: str = "/auth/login",
                 expires: timedelta = timedelta(days=7),
                 refresh_expires: timedelta = timedelta(days=14)) -> None:
        self.security = OAuth2PasswordBearer(token_url)

        from jwt import encode, decode
        self.encoder = encode
        self.decoder = decode

        self.secret = secret
        self.expires = expires
        self.refresh_expires = refresh_expires

    def decode_token(self, token: str) -> dict:
        return self.decoder(token, self.secret, ["HS256"])

    def refresh_token(self, refresh_key: str) -> tuple[str, str] | None:
        try:
            _data = self.decode_token(refresh_key)
        except:
            return None

        if _data.get("type") != "refresh":
            return None

        return self.generate_token(**_data["data"])

    def generate_token(self, user_id: str,
                       roles: list[str] = [],
                       claims: dict[str, Any] = {}) -> tuple[str, str]:

        access_token = self.encoder({"data": {"user_id": user_id, 
                                       "roles": roles,
                                       "claims": claims}, "type": "access", "exp": datetime.utcnow() + self.expires},
                                    self.secret)

        refresh_token = self.encoder({"data": {"user_id": user_id, 
                                       "roles": roles,
                                       "claims": claims}, "type": "refresh", "exp": datetime.utcnow() + self.refresh_expires},
                                     self.secret)

        return access_token, refresh_token
