from typing import Mapping, Sequence, cast
from ascender.core.cli_engine.protos.basic_cli import BasicCLI
from ascender.core.cli_engine.protos.generic_cli import GenericCLI

from ascender.core.cli_engine.types.command_metadata import BasicMetadata_, GenericMetadata_
from ascender.core.cli_engine.types.handler_metadata import HandlerMetadataInfo_
from ascender.core.cli_engine.types.parameter import ParameterInfo
from ascender.core.cli_engine.utils.metadata_from_class import _get_class_parameters
from ascender.core.cli_engine.utils.signature_from_callable import _get_parameters, _signature_from_callable


class Command:
    """
    Decorator for defining a command in the CLI engine.
    
    This decorator is used to register a function as a command that can be executed
    from the command line interface. It supports two types of commands:
    
    - BasicCLI: Single command with one execute() method that handles the command execution.
      Can have optional arguments and positional arguments.
      
    - GenericCLI: Multi-command (group command) that can have multiple functions for 
      different subcommands. Has one base argument (the name of the GenericCLI) and 
      one positional argument (subcommand) that can have multiple positional arguments.
    """
    def __init__(
        self, 
        name: str | None = None, 
        description: str = "",
        help: str | None = "", 
        **kwargs
    ):
        """
        `@Command` decorator's constructor
        
        Args:
            name (str | None): The name of the command. If None, the class name will be used.
            description (str): A brief description of the command.
            help (str | None): Detailed help text for the command.
            **kwargs: Additional keyword arguments to store as metadata.
        """
        self.name = name
        self.description = description
        self.help = help
        self.kwargs = kwargs

    def detect_kind(self, cls: type[BasicCLI | GenericCLI]) -> str:
        """
        Detects whether the decorated class is a BasicCLI or GenericCLI command.
        
        BasicCLI: Single command class that implements execute() method
        GenericCLI: Multi-command group class that can have multiple command methods
        """
        if issubclass(cls, BasicCLI):
            return "basic"
        elif issubclass(cls, GenericCLI):
            return "generic"
        else:
            raise ValueError(f"Command class {cls.__name__} must inherit from either BasicCLI or GenericCLI")

    def parse_parameters(self, cls: type[BasicCLI | GenericCLI]) -> Mapping[str, ParameterInfo] | Sequence[HandlerMetadataInfo_]:
        """
        Parses the parameters of the command class methods.
        
        For BasicCLI, it parses the parameters of the execute() method.
        For GenericCLI, it parses the parameters of each command method.
        """
        kind = self.detect_kind(cls)
        
        match kind:
            case "basic":
                # BasicCLI: parse execute() method parameters
                data = _get_class_parameters(cls)
                return data
                
            case "generic":
                parameters = []
                # GenericCLI: parse each command method parameters
                for attr_name in dir(cls):
                    attr = getattr(cls, attr_name)
                    if callable(attr) and hasattr(attr, "__metadata__"):
                        signature = _signature_from_callable(attr)
                        parameters.append(attr.__metadata__)
                return cast(Sequence[HandlerMetadataInfo_], parameters)
        
        raise ValueError(f"Unknown command kind: {kind}")
        
    def __call__(self, cls: type[BasicCLI | GenericCLI]):
        # Detect the command kind based on inheritance
        kind = self.detect_kind(cls)
        
        if not self.help and cls.__doc__:
            self.help = cls.__doc__.strip()
        
        # For now, store as dict until we fix the metadata system
        # Fuck you copilot!
        if issubclass(cls, BasicCLI):
            cls.__asc_command__ = BasicMetadata_(
                name=self.name or cls.__name__.lower(),
                description=self.description,
                help=self.help,
                kind=kind,
                parameters=cast(Mapping[str, ParameterInfo], self.parse_parameters(cls)), # sometimes python's type checker is so crutchy as hell.
                additional=self.kwargs
            )

        elif issubclass(cls, GenericCLI):
            cls.__asc_command__ = GenericMetadata_(
                name=self.name or cls.__name__.lower(),
                description=self.description,
                help=self.help,
                kind=kind,
                parameters=cast(Sequence[HandlerMetadataInfo_], self.parse_parameters(cls)), # sometimes python's type checker is so crutchy as hell.
                additional=self.kwargs
            )

        return cls