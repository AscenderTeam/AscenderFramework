from __future__ import annotations
from typing import TYPE_CHECKING

from core.extensions.authentication.base_auth import BaseAuthentication
from core.extensions.authentication.custom.provider import AuthenticationProvider

if TYPE_CHECKING:
    from core.application import Application

class AscenderAuthenticationFramework:
    
    application: Application
    auth_provider: AuthenticationProvider | None = None


    @staticmethod
    def run_authentication(app: Application, token_url: str = "/auth/login"):
        AscenderAuthenticationFramework.application = app
        AscenderAuthenticationFramework.auth_provider = BaseAuthentication(token_url)
    
    @staticmethod
    def run_custom_authentication(app: Application, auth_provider: AuthenticationProvider):
        AscenderAuthenticationFramework.application = app
        AscenderAuthenticationFramework.auth_provider = auth_provider
    
    @staticmethod
    def use_authentication_database():
        return "core.extensions.authentication.entity"