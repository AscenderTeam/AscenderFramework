import os
from typing import Literal, Mapping, Sequence

from fastapi import FastAPI
from ascender.abc.middleware import AscenderMiddleware
from ascender.common.api_docs import DefineAPIDocs
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core._config.static_files import configure_staticfile_serving
from ascender.core.cli.main import BaseCLI, GenericCLI
from ascender.core.cli.processor import CLI
from ascender.core.database.engine import DatabaseEngine
from ascender.core.router.graph import RouterGraph


class Application:
    def __init__(
        self,
        router_graph: RouterGraph,
        *,
        cli_settings: Sequence[BaseCLI | GenericCLI] = [],
        docs_settings: DefineAPIDocs = DefineAPIDocs(),
        database_settings: DatabaseEngine | None = None,
        middleware_settings: Sequence[AscenderMiddleware] = []
    ) -> None:
        self.docs_settings = docs_settings
        self.database_settings = database_settings
        self.middleware_settings = middleware_settings

        # :internal:
        self.app = FastAPI(title=self.docs_settings.title, 
                           docs_url=self.docs_settings.swagger_url, 
                           redoc_url=self.docs_settings.redoc_url,
                           description=self.docs_settings.description, 
                           version=_AscenderConfig().get_version())
        
        self.router_graph = router_graph
        
        self.cli_settings = cli_settings

        self.__cli = CLI(self, app_name="AscenderCLI") # type: ignore (temp)
        
        self.__handle_application_settings()
        configure_staticfile_serving(self.app)
    
    def __handle_application_settings(self):
        if self.database_settings is not None:
            self.database_settings.run_database(self.app)
        
        for middleware in self.middleware_settings:
            self.app.add_middleware(middleware)

    def __process_cli_apps(self):
        """
        Registers and runs all provided CLI commands and groups.
        """
        for cli_config in self.cli_settings:
            if isinstance(cli_config, BaseCLI):
                self.__cli.register_base(cli_config.__class__.__name__.removesuffix("CLI").lower(), cli_config) # Use name of class as first argument of command
            
            if isinstance(cli_config, GenericCLI):
                self.__cli.register_generic(cli_config)
    
    def run_cli(self):
        self.__process_cli_apps()
        self.__cli.run()

    def launch(self):
        """
        Launches application in server-mode and builds up fastapi enforcing Uvicorn to handle server part
        """
        os.environ["ASC_MODE"] = "server"
        # Define all CLI applications
        self.run_cli()
        self.router_graph.create_router_graph(self)
        return self.app
    
    def __call__(self):
        self.router_graph.create_router_graph(self)
        return self.app