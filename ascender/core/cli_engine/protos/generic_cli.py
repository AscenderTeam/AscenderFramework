from typing import Any, Mapping

from ascender.core.cli_engine.types.command_metadata import GenericMetadata_


class GenericCLI:
    """
    A base proxy class for defining generic CLI commands.
    
    Generic CLI can have multiple subcommands defined as methods that are wrapped by `@Handler(...)` decorator.

    For more details please refer to [GenericCLI Overview Documentation](/cli/overview#genericcli-commands) and [GenericCLI Examples](/cli/examples#genericcli-examples).
    """
    __asc_command__: GenericMetadata_