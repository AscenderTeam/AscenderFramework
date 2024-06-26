class AuthorizationConstants:
    controllers_path: str = "controllers"
    controller_name: str = "Auth"
    service_name: str = "AuthService"
    repo_name: str = "AuthRepo"

    def __init__(self, controller_name: str = "auth", controllers_path: str = "controllers") -> None:
        self.controllers_path = controllers_path
        self.controller_name = controller_name.capitalize()
        self.service_name = f"{self.controller_name}Service"
        self.repo_name = f"{self.controller_name}Repo"
    
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
        },
        "plugin_configs": {
            # Configuration for plugins here...
        },
    }
""".replace("{controller_name}", self.controller_name).replace("{controller_name_lower}", self.controller_name.lower()).replace("{service_name}", self.service_name).replace("{repo_name}", self.repo_name)

        controller_code = """from fastapi import Depends
from controllers.{lower_controller_name}.models import LoginDTO, UserDTO, UserResponse
from controllers.{lower_controller_name}.repository import {repo_name}
from controllers.{lower_controller_name}.service import {service_name}
from core.extensions.authentication.entity import UserEntity
from core.extensions.serializer import Serializer
from core.guards.authenticator import GetAuthenticatedUser, IsAuthenticated
from core.types import ControllerModule
from core.utils.controller import Controller, Delete, Get, Post
from core.utils.sockets import Listen

@Controller()
class {controller_name}:
    def __init__(self, {lower_controller_name}_service: {service_name}) -> None:
        self.{lower_controller_name}_service = {lower_controller_name}_service

    @Post("login")
    async def login(self, user: LoginDTO):
        return await self.{lower_controller_name}_service.auth_provider.authenticate(user.username, user.password.get_secret_value())

    @Post("register")
    async def register(self, user: UserDTO):
        return await self.{lower_controller_name}_service.create_user(user)

    @Get("me")
    async def get_auth_endpoint(self, user: UserEntity = Depends(GetAuthenticatedUser(True))):
        return Serializer(UserResponse, user)()

    @Delete("[user_id]", dependencies=[Depends(IsAuthenticated(True))])
    async def delete_user_endpoint(self, user_id: int):
        return await self.{lower_controller_name}_service.delete_user(user_id)

    ## SocketIO authentication support... In case of using SocketIO, uncomment the following code
    ## To enable SocketIO support, add this piece of code `app.use_sio()` in `bootstrap.py`
    # @Listen("connect", all_namespaces=True)
    # @IsAuthenticatedSocket()
    # async def socket_auth_endpoint(self, ctx):
    #     await ctx.emit("status", "Successfully connected")

{setup_code}
""".format(controller_name=self.controller_name, lower_controller_name=self.controller_name.lower(), service_name=self.service_name, repo_name=self.repo_name, setup_code=setup_code).replace("[user_id]", "{user_id}")

        return controller_code
    
    def get_service_file(self) -> str:
        return """from controllers.{lower_controller_name}.models import UserDTO, UserResponse
from core.extensions.authentication import AscenderAuthenticationFramework
from core.extensions.serializer import Serializer
from core.extensions.services import Service
from controllers.{lower_controller_name}.repository import {repo_name}


class {service_name}(Service):

    def __init__(self, repository: {repo_name}) -> None:
        self._repository = repository
        self.auth_provider = AscenderAuthenticationFramework.auth_provider
    
    async def create_user(self, dto: UserDTO):
        user = await self.auth_provider.create_user(dto.username, dto.password.get_secret_value())
        
        user = await self._repository.update_user_from_entity(user, email=dto.email)
        response = Serializer(UserResponse, user)
        return response()
    
    async def delete_user(self, user_id: str):
        user = await self.auth_provider.get_user(user_id)
        if not user:
            return False
        
        return await self._repository.delete_user(user)
""".format(lower_controller_name=self.controller_name.lower(), service_name=self.service_name, repo_name=self.repo_name)

    def get_models_file(self) -> str:
        return """from datetime import datetime
from typing import Optional
from pydantic import BaseModel, SecretStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserDTO(BaseModel):
    username: str
    password: SecretStr
    email: str

class LoginDTO(BaseModel):
    username: str
    password: SecretStr
"""

    def get_repository_file(self) -> str:
        return """# from entities.[your_entity] import [YourEntity]Entity
from core.extensions.authentication.entity import UserEntity
from core.extensions.repositories import Repository


class {repo_name}(Repository):
    def __init__(self) -> None:
        \"""
        Define your repository here

        Name of entities that were set in `def setup()` in endpoints.py file are will passed into __init__ here
        Note that if you are not using entities that were added in `def setup()` then remove it from there also, or else you will receive error
        \"""
        # def __init__(self, [your_entity]: YourEntity]Entity) -> None:
        #   self.[your_entity] = [your_entity]

    async def update_user_from_entity(self, entity: UserEntity, **kwargs) -> UserEntity:
        \"""
        Update user from entity

        :param entity: UserEntity
        :param kwargs: Any
        :return: UserEntity
        \"""
        query = entity.update_from_dict(kwargs)

        await query.save()
        return query
    
    async def delete_user(self, entity: UserEntity):
        \"""
        Delete user

        :param user_id: str
        :return: bool
        \"""
        return await entity.delete()
        """.format(repo_name=self.repo_name)

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
                "content": self.get_repository_file()
            },
            {
                "name": "repository.py",
                "path": "{0}/{1}/models.py".format(self.controllers_path, self.controller_name.lower()),
                "content": self.get_models_file()
            }
        ]

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
        },
        "plugin_configs": {
            # Configuration for plugins here...
        },
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
    \"""
    Define your repository here
    As you import your entities, you can use them here, check up setup() in endpoints.py file
    As you define there entities `keyword: entitytype` you can use them here as `keyword` and `entitytype`
    \"""
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
