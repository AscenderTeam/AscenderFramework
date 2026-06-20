import os
from collections import defaultdict
from typing import Any, Callable, Iterable, Sequence

from fastapi import FastAPI

from ascender.abc.middleware import AscenderMiddleware
from ascender.common.api_docs import DefineAPIDocs
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core._config.static_files import configure_staticfile_serving
from ascender.core.applications._lifespan import create_lifespan
from ascender.core.applications.root_injector import RootInjector
from ascender.core.cli_engine import BasicCLI, CLIEngine, GenericCLI
from ascender.core.database.engine import DatabaseEngine
from ascender.core.errors.lifecycle_error import LifecycleError
from ascender.core.logger._logger import configure_logger
from ascender.core.router.graph import RouterGraph
from ascender.core.services import LifecycleService


class Application:
    def __init__(
        self,
        router_graph: RouterGraph,
        *,
        cli_settings: Sequence[BasicCLI | GenericCLI] = [],
        docs_settings: DefineAPIDocs = DefineAPIDocs(),
        database_settings: DatabaseEngine | None = None,
        middleware_settings: Sequence[AscenderMiddleware] | AscenderMiddleware = [],
    ) -> None:
        self.docs_settings = docs_settings
        self.database_settings = database_settings
        self.middleware_settings = (
            middleware_settings
            if isinstance(middleware_settings, Iterable)
            else [middleware_settings]
        )

        main_payload = dict(
            title=self.docs_settings.title,
            docs_url=self.docs_settings.swagger_url,
            redoc_url=self.docs_settings.redoc_url,
            debug=_AscenderConfig().get_environment().debug,
            description=self.docs_settings.description,
            version=_AscenderConfig().get_version(),
        )

        if not hasattr(FastAPI, "add_event_handler"):
            self.app = FastAPI(
                **main_payload,  # pyright: ignore
                lifespan=create_lifespan(self),
            )
        else:
            self.app = FastAPI(**main_payload)  # pyright: ignore

        self.router_graph = router_graph

        self.cli_settings = cli_settings

        cli_name = os.getenv("ASC_CLI_NAME", "ascender run")

        self.__cli = CLIEngine(
            commands=self.cli_settings,
            usage=f"{cli_name} <command> [options]",
            description="🚀 Ascender Framework - Modern Python Web Framework",
        )

        self.events = defaultdict(list)

        # Guards the one-time boot pipeline (see `bootstrap`). The uvicorn
        # `factory=True` entrypoint may invoke us more than once across workers/
        # imports; the routes and lifecycle must only be wired up once.
        self._booted = False

        self.__handle_application_settings()
        configure_staticfile_serving(self.app)

    def __handle_application_settings(self):
        if self.database_settings is not None:
            self.database_settings.run_database(self)

        for middleware in self.middleware_settings:
            self.app.add_middleware(middleware)  # type: ignore

    def is_ok(self) -> bool:
        """
        Checks if the application has been properly initialized with a root injector.

        Returns
        -------
        bool
            True if the application is properly initialized, False otherwise.
        """
        return bool(RootInjector()._injector)

    def add_event_handler(self, event: str, callback: Callable[..., Any]):
        if hasattr(FastAPI, "add_event_handler"):
            # For type checker we remove attribute to avoid false positive
            self.app.add_event_handler(event, callback)  # pyright: ignore[reportAttributeAccessIssue] noqa: E501
            return

        self.events[event].append(callback)

    def run_cli(self):
        # self.__process_cli_apps()
        # self.__cli.run()
        return self.__cli()

    def start_lifecycle(self):
        raw_providers = (
            RootInjector().get("LIFECYCLE_TOKENS", None, options={"optional": True})
            or []
        )

        providers = []
        for p in raw_providers:
            if isinstance(p, list):
                providers.extend(p)
            else:
                providers.append(p)

        if not providers:
            return

        for provider in providers:
            service = RootInjector().get(
                provider, not_found_value=None, options={"optional": True}
            )
            if service is None:
                raise LifecycleError(f"Lifecycle service {provider} not found")

            if isinstance(service, LifecycleService):
                self.add_event_handler("startup", service.on_startup)
                self.add_event_handler("shutdown", service.on_shutdown)

    def launch(self):
        """
        Launches application in server-mode and builds up fastapi enforcing Uvicorn to handle server part
        """
        os.environ["ASC_MODE"] = "server"

        # Define all CLI applications
        self.run_cli()
        # self.router_graph.create_router_graph(self)
        return self.app

    def bootstrap(self) -> FastAPI:
        """
        The explicit, ordered server boot pipeline — the single place that reads
        top-to-bottom as "what happens at startup".

        Idempotent: the first call wires everything up, subsequent calls are a
        no-op and just return the built ASGI app. This used to live (unnamed and
        unguarded) inside `__call__`, where mounting the routes was a hidden side
        effect of uvicorn invoking the factory.

        Sequence:
            1. Resolve environment + configure logging.
            2. Register lifecycle (startup/shutdown) handlers.
            3. Mount the router graph onto FastAPI.
        """
        if self._booted:
            return self.app

        # 1. Environment + logging
        environment = _AscenderConfig().get_environment()
        self.start_lifecycle()
        logger = configure_logger(_AscenderConfig().config.logging)
        logger.setLevel(environment.logging.upper())

        # 2. Mount the route graph onto FastAPI
        self.router_graph.create_router_graph(self)

        self._booted = True
        return self.app

    def __call__(self) -> FastAPI:
        # Uvicorn `factory=True` entrypoint — delegates to the explicit, idempotent
        # boot pipeline rather than carrying the startup logic itself.
        return self.bootstrap()
