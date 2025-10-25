from typing import Any, Mapping

from ascender.core.cli_engine.types.command_metadata import BasicMetadata_


class BasicCLI:
    """
    A base proxy class for defining basic CLI commands.

    For more details please refer to [BasicCLI Overview Documentation](/cli/overview#basiccli-commands) and [BasicCLI Examples](/cli/examples#basiccli-examples).
    """
    __asc_command__: BasicMetadata_
    
    def execute(self) -> None:
        """
        Method to be implemented by subclasses to execute the command logic.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Execute method must be implemented by BasicCLI subclasses.")