from ascender.core.cli_engine import BasicCLI, GenericCLI
from ascender.core import Provider


def useCLI(command: type[GenericCLI] | type[BasicCLI]) -> Provider:
    return {
        "provide": "ASC_CLI_COMMAND",
        "use_class": command,
        "multi": True
    }