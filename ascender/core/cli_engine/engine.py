from argparse import ArgumentParser
from typing import Any, Sequence

from codetiming import Timer

from ascender.core.cli_engine.protos.generic_cli import GenericCLI
from ascender.core.cli_engine.protos.basic_cli import BasicCLI




class CLIEngine:
    def __init__(
        self,
        commands: Sequence[type[GenericCLI | BasicCLI]] | None = None,
        usage: str | None = None,
        description: str | None = None
    ) -> None:
        """
        Ascender Framework's CLI Engine represents the command-line interface for the framework.
        It allows users to interact with the framework through command-line commands and parameters.
        
        Also providing them OOP-like interface to define their custom `ascender` commands.
        
        It consists of two main components:
        1. **BasicCLI**: These are the command-line basic classbased commands that can be executed directly only one command (with argument or not).
        2. **GenericCLI**: These are the generic commands that can be used to create groups of commands.
        """
        self.parser = ArgumentParser(
            "Ascender Framework CLI", 
            usage=usage,
            description=description
        )
    
    @Timer("CLIEngine.process_commands", text="Elapsed time: {:.2f} ms")
    def process_commands(self, commands: Sequence[Any]):
        for command in commands:
            pass
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass