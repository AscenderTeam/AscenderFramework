from __future__ import annotations
import os
from typing import TYPE_CHECKING

from ascender.clis.tests.tests_app import TestRunnerCLI

from .root_injector import RootInjector

if TYPE_CHECKING:
    from ascender.core.di.interface.provider import Provider


def createInternalApplication():
    """
    Runs application in CLI mode
    
    Args:
        config: An optional list of providers for root-level configuration.
        
    Returns:
        An initialized Application instance.
    """
    from ascender.clis.new.new_app import NewCLI
    from ascender.clis.run.run_app import RunCLI
    from ascender.clis.version.version_app import VersionCLI
    from ascender.clis.generator.generator_app import GeneratorCLI
    
    from ascender.core.cli_engine import CLIEngine, useCLI
    
    
    os.environ["ASC_MODE"] = "cli"
    # Initialize the root injector
    root_injector = RootInjector()

    # Internal providers necessary for Application creation
    internal_providers: list["Provider"] = [
        useCLI(GeneratorCLI),
        useCLI(NewCLI),
        useCLI(RunCLI),
        useCLI(VersionCLI),
        useCLI(TestRunnerCLI),
        {
            "provide": CLIEngine,
            "use_factory": lambda commands: CLIEngine(commands, usage="ascender <command> [options]", description="🚀 Ascender Framework - Modern Python Web Framework"),
            "deps": ["ASC_CLI_COMMAND"]
        },
    ]

    # Configuration-based application creation
    root_injector.create(internal_providers)

    return root_injector.get(CLIEngine) # type: ignore