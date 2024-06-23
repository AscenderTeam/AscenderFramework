from core.cli_apps.controller_cli.cli_processor import ControllerCLI
from core.cli_apps.migrate_cli import MigrateCLI
from core.cli_apps.users_cli import UsersCLI
from core.extensions.authentication import AscenderAuthenticationFramework
from importlib import import_module
from fastapi import FastAPI
from typing import Any, Callable, List

import uvicorn
from core.cli.processor import CLI
from core.cli_apps.serve_cli import BuildControlCLI, ServerControlCLI
from core.extensions.authentication.custom.provider import AuthenticationProvider
from core.loader import Loader
from core.plugins.plugin import Plugin
from core.plugins.plugin_loader import PluginLoader
from core.sockets import SocketIOApp

from core.types import Controller


class Application:
    def __init__(self, 
                controllers: List[Controller] = [],
                on_server_start: Callable[['Application'], None] | None = None, 
                on_server_runtime_error: Callable[[Exception], None] | None = None,
                on_cli_run: Callable[['Application', CLI], None] | None = None,
                on_injections_run: Callable[['Application'], None] | None = None,
                on_event_start: Callable[['Application', List[object]], None] | None = None,
                on_event_shutdown: Callable[['Application', List[object]], None] | None = None) -> None:
        self.app = FastAPI(title="Ascender Framework API")
        self.socketio: SocketIOApp | None = None

        self._on_server_start = on_server_start
        self._on_server_runtime_error = on_server_runtime_error
        self._on_cli_run = on_cli_run
        self._on_injections_run = on_injections_run
        self._on_event_start = on_event_start
        self._on_event_shutdown = on_event_shutdown
        
        # Initialize Plugin Loader Module
        self._plugin_loader = PluginLoader(self)

        self.loader_module = Loader(self.app, self, controllers, self._plugin_loader)
        
        # Initialize CLI module
        self.__cli = CLI(self, app_name="AscCLI")

    def test_callback(self, *args, **kwargs):
        print(*args, **kwargs)

    def use_database(self):
        module = import_module("core.database")

        module.run_database(self.app)
    
    async def use_database_cli(self):
        module = import_module("core.database")

        await module.run_database_cli()

    def add_middleware(self, middleware: type, **options) -> None:
        self.app.add_middleware(middleware, **options)

    def run_cli(self) -> None:
        
        if self._on_cli_run is not None:
            self._on_cli_run(self, self.__cli)

        self.__cli.register_base("serve", ServerControlCLI())
        self.__cli.register_base("build", BuildControlCLI())

        self.__cli.register_generic(UsersCLI())
        self.__cli.register_generic(MigrateCLI())
        self.__cli.register_generic(ControllerCLI())
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
        return "v1.1.1"
    
    def use_authentication(self, token_url: str = "/auth/login"):
        AscenderAuthenticationFramework.run_authentication(self, token_url=token_url)
    
    def use_custom_authentication(self, auth_provider: AuthenticationProvider):
        AscenderAuthenticationFramework.run_custom_authentication(self, auth_provider)

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
        
        return self.app