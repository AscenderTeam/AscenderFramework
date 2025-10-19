import os
from typing import Sequence
from ascender.clis.generator.generator_app import GeneratorCLI
from ascender.clis.new.new_app import NewCLI
from ascender.clis.run.run_app import RunCLI
from ascender.core.cli.main import BaseCLI, GenericCLI
from ascender.core.cli.processor import CLI
from ascender.core.cli.provider import provideCLI
from .root_injector import RootInjector
from ascender.core.di.interface.provider import Provider


def cli_factory(cli_settings: Sequence[BaseCLI | GenericCLI]):
    _cli = CLI(None)
    for cli_config in cli_settings:
        if isinstance(cli_config, BaseCLI):
            _cli.register_base(cli_config.__class__.__name__.removesuffix("CLI").lower(), cli_config) # Use name of class as first argument of command
            
        if isinstance(cli_config, GenericCLI):
            _cli.register_generic(cli_config)
    
    return _cli


def createInternalApplication() -> CLI:
    """
    Runs application in CLI mode
    
    Args:
        config: An optional list of providers for root-level configuration.
        
    Returns:
        An initialized Application instance.
    """
    os.environ["ASC_MODE"] = "cli"
    # Initialize the root injector
    root_injector = RootInjector()

    # Internal providers necessary for Application creation
    internal_providers: list[Provider] = [
        provideCLI(GeneratorCLI),
        provideCLI(NewCLI),
        provideCLI(RunCLI),
        {
            "provide": CLI,
            "use_factory": cli_factory,
            "deps": ["CLI_INTERFACE"]
        },
    ]

    # Configuration-based application creation
    root_injector.create(internal_providers)
    
    return root_injector.get(CLI) # type: ignore