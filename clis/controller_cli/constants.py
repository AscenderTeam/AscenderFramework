class ControllerConstants:
    controllers_path: str = "controllers"
    controller_name: str
    service_name: str
    repo_name: str

    def __init__(self, controller_name: str, controllers_path: str = "controllers") -> None:
        self.controller_name = controller_name.capitalize()
        self.service_name = f"{self.controller_name}Service"
        self.repo_name = f"{self.controller_name}Repo"

        self.controllers_path = controllers_path

    def get_controller_file(self) -> str:
        setup_code = """
def setup() -> ControllerModule:
    return {
        "controller": {controller_name},
        "services": {
            "{controller_name_lower}": {service_name}
        },
        "repository": {repo_name},
        "repository_entities": {
            # Add your entities here...
        }
    }
""".replace("{controller_name}", self.controller_name).replace("{controller_name_lower}", self.controller_name.lower()).replace("{service_name}", self.service_name).replace("{repo_name}", self.repo_name)
        return f"""
from {self.controllers_path}.{self.controller_name.lower()}.repository import {self.repo_name}
from {self.controllers_path}.{self.controller_name.lower()}.service import {self.service_name}
from core.types import ControllerModule
from core.utils.controller import Controller, Get

@Controller()
class {self.controller_name}:
    def __init__(self, {self.controller_name.lower()}_service: {self.service_name}) -> None:
        self.{self.controller_name.lower()}_service = {self.controller_name.lower()}_service

    @Get()
    async def get_{self.controller_name.lower()}_endpoint(self):
        return self.{self.controller_name.lower()}_service.get_hello()
\n
""" + setup_code

    def get_service_file(self) -> str:
        return f"""
from core.extensions.services import Service
from {self.controllers_path}.{self.controller_name.lower()}.repository import {self.repo_name}


class {self.service_name}(Service):

    def __init__(self, repository: {self.repo_name}) -> None:
        self._repository = repository
    
    def get_hello(self):
        return "Hello World!"
"""

    def get_repo_file(self) -> str:
        return f"""
# from entities.[your_entity] import [YourEntity]Entity
from core.extensions.repositories import Repository


class {self.repo_name}(Repository):
    def __init__(self) -> None:
        \"""
        Define your repository here

        Name of entities that were set in `def setup()` in endpoints.py file are will passed into __init__ here
        Note that if you are not using entities that were added in `def setup()` then remove it from there also, or else you will receive error
        \"""
        # def __init__(self, [your_entity]: YourEntity]Entity) -> None:
        #   self.[your_entity] = [your_entity]
"""

    def get_mandatory_files(self):
        return [
            {
                "name": "endpoints.py",
                "path": "{0}/{1}/endpoints.py".format(self.controllers_path, self.controller_name.lower()),
                "content": self.get_controller_file()
            },
            {
                "name": "service.py",
                "path": "{0}/{1}/service.py".format(self.controllers_path, self.controller_name.lower()),
                "content": self.get_service_file()
            },
            {
                "name": "repository.py",
                "path": "{0}/{1}/repository.py".format(self.controllers_path, self.controller_name.lower()),
                "content": self.get_repo_file()
            }
        ]

    def get_optional_files(self):
        return [
            {
                "name": "models.py",
                "path": "{0}/{1}/models.py".format(self.controllers_path, self.controller_name.lower()),
                "content": ""
            },
            {
                "name": "serializers.py",
                "path": "{0}/{1}/serializers.py".format(self.controllers_path, self.controller_name.lower()),
                "content": ""
            }
        ]
