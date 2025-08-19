from ascender.core.cli_engine.protos.basic_cli import BasicCLI
from ascender.core.cli_engine.protos.generic_cli import GenericCLI


class Command:
    """
    Decorator for defining a command in the CLI engine.
    
    This decorator is used to register a function as a command that can be executed
    from the command line interface. It allows for specifying various attributes of the
    command such as its name, description, and parameters.
    """
    def __init__(
        self, 
        name: str | None = None, # The name of the command, used as positional argument in CLI. 
        description: str = "", # A brief description of the command, used for help messages.
        **kwargs
    ):
        self.name = name
        self.description = description
        self.kwargs = kwargs

    def detect_kind(self, cls: type[BasicCLI | GenericCLI]):
        if isinstance(cls, BasicCLI):
            pass
    
    def __call__(self, cls):
        # Register the command with the CLI engine
        # This is where you would add the logic to register the command
        cls._command_info = {
            "name": self.name or cls.__name__,
            "description": self.description,
            "parameters": [],
            **self.kwargs
        }
        
        return cls