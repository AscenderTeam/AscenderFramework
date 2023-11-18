from core.cli_apps.users_cli import UsersCLI
from core.extensions.authentication import AscenderAuthenticationFramework
from importlib import import_module
from fastapi import FastAPI
from typing import Callable, List

import uvicorn
from core.cli.main import CLI
from core.cli_apps.core_updater.updater_cli import UpdaterCLI
from core.cli_apps.serve_cli import Serve
from core.extensions.authentication.custom.provider import AuthenticationProvider
from core.loader import Loader

from core.types import Controller

class Application:
    def __init__(self, 
                controllers: List[Controller] = [],
                on_server_start: Callable[['Application'], None] | None = None, 
                on_server_runtime_error: Callable[[Exception], None] | None = None,
                on_cli_run: Callable[['Application', CLI], None] | None = None) -> None:
        self.app = FastAPI(title="Ascender Framework API")

        self._on_server_start = on_server_start
        self._on_server_runtime_error = on_server_runtime_error
        self._on_cli_run = on_cli_run
        
        self.loader_module = Loader(self.app, controllers)
        
        # Initialize CLI module
        self.__cli = CLI(self, "AscCLI", "CLI for Python")
    
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

        self.__cli.register_command(Serve())
        
        self.__cli.register_generic_command(UpdaterCLI())
        self.__cli.register_generic_command(UsersCLI())
        self.__cli.run()
    
    def run_server(self, host: str, port: int) -> Callable | None:
        try:
            if self._on_server_start is not None:
                self._on_server_start(self)
            uvicorn.run(app=self.app, host=host, port=port)
            
        except Exception as e:
            # Call hooked exception handler if exists
            if self._on_server_runtime_error is not None:
                self._on_server_runtime_error(e)
            
            raise e
    
    def get_version(self) -> str:
        return "v0.0.1"
    
    def use_authentication(self, token_url: str = "/auth/login"):
        AscenderAuthenticationFramework.run_authentication(self, token_url=token_url)
    
    def use_custom_authentication(self, auth_provider: AuthenticationProvider):
        AscenderAuthenticationFramework.run_custom_authentication(self, auth_provider)
