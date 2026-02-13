from ascender.core.services import LifecycleService
import os
from typing import Iterable, Sequence

from fastapi import FastAPI
from ascender.abc.middleware import AscenderMiddleware
from ascender.common.api_docs import DefineAPIDocs
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core._config.static_files import configure_staticfile_serving
from ascender.core.applications.root_injector import RootInjector
from ascender.core.cli_engine import CLIEngine, BasicCLI, GenericCLI
from ascender.core.database.engine import DatabaseEngine
from ascender.core.logger._logger import configure_logger
from ascender.core.router.graph import RouterGraph
from ascender.core.errors.lifecycle_error import LifecycleError


class Application:
    def __init__(
        self,
        router_graph: RouterGraph,
        *,
        cli_settings: Sequence[BasicCLI | GenericCLI] = [],
        docs_settings: DefineAPIDocs = DefineAPIDocs(),
        database_settings: DatabaseEngine | None = None,
        middleware_settings: Sequence[AscenderMiddleware] | AscenderMiddleware = []
    ) -> None:
        self.docs_settings = docs_settings
        self.database_settings = database_settings
        self.middleware_settings = middleware_settings if isinstance(middleware_settings, Iterable) else [middleware_settings]

        # :internal:
        self.app = FastAPI(title=self.docs_settings.title,  # type: ignore
                           docs_url=self.docs_settings.swagger_url, 
                           redoc_url=self.docs_settings.redoc_url,
                           debug=_AscenderConfig().get_environment().debug,
                           description=self.docs_settings.description, 
                           version=_AscenderConfig().get_version())
        
        self.router_graph = router_graph
        
        self.cli_settings = cli_settings

        self.__cli = CLIEngine(commands=self.cli_settings, usage="ascender <command> [options]", description="🚀 Ascender Framework - Modern Python Web Framework")
        
        self.__handle_application_settings()
        configure_staticfile_serving(self.app)
    
    def __handle_application_settings(self):
        if self.database_settings is not None:
            self.database_settings.run_database(self.app)
        
        for middleware in self.middleware_settings:
            self.app.add_middleware(middleware) # type: ignore

    def is_ok(self) -> bool:
        """
        Checks if the application has been properly initialized with a root injector.

        Returns
        -------
        bool
            True if the application is properly initialized, False otherwise.
        """
        return bool(RootInjector()._injector)

    def run_cli(self):
        # self.__process_cli_apps()
        # self.__cli.run()
        return self.__cli()

    def start_lifecycle(self):
        raw_providers = RootInjector().get("LIFECYCLE_TOKENS", None, options={"optional": True}) or []

        providers = []
        for p in raw_providers:
            if isinstance(p, list):
                providers.extend(p)
            else:
                providers.append(p)

        if not providers:
            return
        
        for provider in providers:
            service = RootInjector().get(provider, not_found_value=None, options={"optional": True})
            if service is None:
                raise LifecycleError(f"Lifecycle service {provider} not found")
            
            if isinstance(service, LifecycleService):
                self.app.add_event_handler("startup", service.on_startup)
                self.app.add_event_handler("shutdown", service.on_shutdown)

    def launch(self):
        """
        Launches application in server-mode and builds up fastapi enforcing Uvicorn to handle server part
        """
        os.environ["ASC_MODE"] = "server"

        # Define all CLI applications
        self.run_cli()
        # self.router_graph.create_router_graph(self)
        return self.app
    
    def __call__(self):
        # # Enviornment configuration
        environment = _AscenderConfig().get_environment()
        self.start_lifecycle()
        # # Configure logger
        logger = configure_logger(_AscenderConfig().config.logging)
        logger.setLevel(environment.logging.upper())

        self.router_graph.create_router_graph(self)
        return self.app