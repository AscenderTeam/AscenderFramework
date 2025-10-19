from typing import Any, Sequence
from ascender.core.cli.main import BaseCLI, GenericCLI
from ascender.core.di.interface.provider import Provider


def provideCLI(
    cli_app: type[GenericCLI] | type[BaseCLI],
) -> Provider:
    return {
        "provide": "CLI_INTERFACE",
        "multi": True,
        "use_class": cli_app,
    }