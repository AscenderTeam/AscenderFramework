from core.cli_apps.controllers_manager.app import ControllersManagerCLI
from core.cli_apps.migrate_cli import MigrateCLI
from core.database.engine import DatabaseEngine
from core.database.types.orm_enum import ORMEnum
from core.extensions.authentication import AscenderAuthenticationFramework
from importlib import import_module
from fastapi import FastAPI
from typing import Any, Callable, List, Literal

import uvicorn
from core.cli.processor import CLI
from core.cli_apps.serve_cli import BuildControlCLI, ServerControlCLI
from core.extensions.authentication.custom.provider import AuthenticationProvider
from core.extensions.repositories import IdentityRepository
from core.identity.manager import IdentityManager
from core.identity.security import Security
from core.identity.singleton import SecuritySingleton
from core.loader import Loader
from core.plugins.plugin import Plugin
from core.plugins.plugin_loader import PluginLoader
from core.registries.service import ServiceRegistry
from core.sockets import SocketIOApp

from core.types import Controller
from settings import DOCS_URLS


class Application:
    def __init__(self, 
                controllers: List[Controller] = [],
                on_server_start: Callable[['Application'], None] | None = None, 
                on_server_runtime_error: Callable[[Exception], None] | None = None,
                on_cli_run: Callable[['Application', CLI], None] | None = None,
                on_injections_run: Callable[['Application'], None] | None = None) -> None:
        self.app = FastAPI(title="Ascender Framework API", 
                           docs_url=DOCS_URLS["swagger"],
                           redoc_url=DOCS_URLS["redoc"])
        self.socketio: SocketIOApp | None = None

        self.service_registry = ServiceRegistry()
        self._on_server_start = on_server_start
        self._on_server_runtime_error = on_server_runtime_error
        self._on_cli_run = on_cli_run
        self._on_injections_run = on_injections_run
        
        # Initialize Plugin Loader Module
        self._plugin_loader = PluginLoader(self)

        self.loader_module = Loader(self.app, self, controllers, self._plugin_loader)
        self.security = None
        
        # Initialize CLI module
        self.__cli = CLI(self, app_name="AscCLI")

    def setup_docs(self, title: str | None = None,
                   description: str | None = None,
                   **options):
        
        params = {
            "title": title,
            "description": description,
            **options
        }

        for param_key, param_value in params.items():
            if param_key in ["title", "description"]:
                if param_value is not None:
                    setattr(self.app, param_key, param_value)
                
                continue

            setattr(self.app, param_key, param_value)


    def use_database(self, logical_o: Callable[[DatabaseEngine], None], orm: ORMEnum, configuration: dict):
        # module = import_module("core.database")

        # module.run_database(self.app)
        database = DatabaseEngine(self.app, orm, configuration)
        self.service_registry.add_singletone(DatabaseEngine, database)
        logical_o(database)

    def add_middleware(self, middleware: type, **options) -> None:
        self.app.add_middleware(middleware, **options)

    def run_cli(self) -> None:
        if self._on_cli_run is not None:
            self._on_cli_run(self, self.__cli)

        self.__cli.register_base("serve", ServerControlCLI)
        self.__cli.register_base("build", BuildControlCLI)

        # self.__cli.register_generic(UsersCLI)
        self.__cli.register_generic(MigrateCLI)
        self.__cli.register_generic(ControllersManagerCLI)
        self.__cli.run()
    
    def run_server(self, host: str, port: int) -> Callable | None:
        try:
            # if self._on_server_start is not None:
                # self._on_server_start(self)
            uvicorn.run("start:app", host=host, port=port, reload=True)
            
        except Exception as e:
            # Call hooked exception handler if exists
            if self._on_server_runtime_error is not None:
                self._on_server_runtime_error(e)
            
            raise e
    
    def get_version(self) -> str:
        return "v1.2.1"
    
    def use_authentication(self, token_url: str = "/auth/login"):
        AscenderAuthenticationFramework.run_authentication(self, token_url=token_url)
    
    def use_custom_authentication(self, auth_provider: AuthenticationProvider):
        AscenderAuthenticationFramework.run_custom_authentication(self, auth_provider)

    def add_authorization(self, logical_o: Callable[[Security], None],
                          identity_repository: IdentityRepository,
                          auth_scheme: Literal["basic", "apikey", "oauth2", "cookie"] = "basic",
                          *scheme_args, **scheme_kargs):
        self.security = SecuritySingleton(Security(identity_repository=identity_repository,
                                 auth_scheme=auth_scheme,
                                 *scheme_args, **scheme_kargs))
        self.service_registry.add_singletone(IdentityManager, IdentityManager(self.security.engine))
        logical_o(self.security)

    def use_sio(self, **options):
        """
        ## Use SocketIO

        Args:
            use_threading (bool, optional): Determine whether it should launch multiprocessingly or not. Defaults to True.
        """
        self.socketio = SocketIOApp(self, **options)
    
    def use_plugin(self, plugin: Plugin):
        self._plugin_loader.use_plugin(plugin)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self._on_server_start is not None:
            if self._on_injections_run is not None:
                self._on_injections_run(self)
            self._on_server_start(self)
        self.app.add_event_handler("startup", self.loader_module.initialize_dependencies)
        return self.app