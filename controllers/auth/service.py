
from core.extensions.services import Service
from controllers.auth.repository import AuthRepo


class AuthService(Service):

    def __init__(self, repository: AuthRepo) -> None:
        self._repository = repository
    
    def get_hello(self):
        return "Hello World!"
