from ascender.clis.builder.build_app import BuildCLI
from ascender.clis.generator.generator_app import GeneratorCLI
from ascender.clis.new.new_app import NewCLI
from ascender.clis.run.run_app import RunCLI
from ascender.clis.serve.serve_app import ServeCLI
from ascender.common.api_docs import DefineAPIDocs
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.cli.provider import provideCLI
from ascender.core.database.engine import DatabaseEngine
from ascender.core.di.abc.base_injector import Injector
from ascender.core.logger._logger import configure_logger, configure_uvicorn_logger
from ascender.core.router.graph import RouterGraph
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.types import IBootstrap
from .application import Application
from .root_injector import RootInjector
from ascender.core.di.interface.provider import Provider


def createApplication(
    app_module: type[AscModuleRef] | None = None, 
    config: IBootstrap | None = None
) -> Application:
    """
    Creates an Application instance based on the provided app module or configuration.
    
    Args:
        app_module: An optional application module implementing AscModuleRef.
        config: An optional list of providers for root-level configuration.
        
    Returns:
        An initialized Application instance.
    
    Raises:
        ValueError: If both `app_module` and `config` are None or specified at the same time.
    """
    # Initialize the root injector
    root_injector = RootInjector()

    # Enviornment configuration
    environment = _AscenderConfig().get_environment()

    # Configure logger
    logger = configure_logger(_AscenderConfig().config.logging)
    logger.setLevel(environment.logging.upper())

    # Internal providers necessary for Application creation
    internal_providers: list[Provider] = [
        provideCLI(BuildCLI),
        provideCLI(GeneratorCLI),
        provideCLI(NewCLI),
        provideCLI(RunCLI),
        provideCLI(ServeCLI),
        {
            "provide": Application,
            "use_factory": lambda graph, cli, docs, injector: Application(
                graph,
                cli_settings=cli, 
                docs_settings=docs,
                database_settings=injector.get(DatabaseEngine, not_found_value=None, options={
                    "optional": True
                }),
                middleware_settings=injector.get("ASC_MIDDLEWARE", not_found_value=[])
            ),
            "deps": [RouterGraph, "CLI_INTERFACE", DefineAPIDocs, Injector]
        },
        {
            "provide": "ASC_LOGGER",
            "value": logger
        }
    ]

    if app_module is None and config is not None:
        # Configuration-based application creation
        root_injector.create(config["providers"] + internal_providers)

        return root_injector.get(Application)  # type: ignore

    if config is None and app_module is not None:
        # print(app_module.__asc_module__.providers)
        root_injector.create(app_module.__asc_module__.providers + internal_providers)
        # app_module.__asc_module__.providers = []
        # Module-based application creation
        if not root_injector.injector:
            raise RuntimeError("Root injector is not initialized.")

        app_injector = app_module.__asc_module__.create_module(root_injector.existing_injector)
        return app_injector._injector.get(Application)  # type: ignore

    # Invalid argument combination
    raise ValueError(
        "Invalid arguments: Either `app_module` or `config` must be provided, but not both."
    )