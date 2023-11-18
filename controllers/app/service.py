from core.extensions.services import Service
from controllers.app.repository import AppRepo


class AppService(Service):

    def __init__(self, repository: AppRepo) -> None:
        self._repository = repository
    
    def get_hello(self):
        return "Yay! It works! Now you can manage your controller by editing `controllers/app/service.py`, HAPPY CODING! :)"
