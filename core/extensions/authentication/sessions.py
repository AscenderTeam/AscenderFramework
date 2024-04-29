from datetime import datetime, timedelta, UTC
import os

import jwt
from core.extensions.authentication.entity import UserEntity


class SessionManager:

    def create_session(self, user: UserEntity, life_time: timedelta) -> str:
        # Generate token: Generates UUID4 token for session
        expiration_time = datetime.now(UTC) + timedelta(hours=1)  # Expires in 1 hour
        payload = {"user": user.id, 'exp': expiration_time}

        # Generate the JWT token
        token = jwt.encode(payload, os.getenv("ASC_SECRETKEY"), algorithm='HS256')
        return token
    
    def get_session(self, token: str) -> str:
        session_data = jwt.decode(token, os.getenv("ASC_SECRETKEY"), algorithms=['HS256'])

        return session_data