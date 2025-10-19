from rich import print as cprint

class DeclaredBaseCliIsNotDefined(Exception):
    def __init__(self, cli_name: str) -> None:
        self.cli_name = cli_name

    def __str__(self) -> str:
        return f"Declared Base Cli returned error on registering cli. BaseCli is not subclass of {self.cli_name}"


class DeclaredGenericCliIsNotDefined(Exception):
    def __init__(self, cli_name: str) -> None:
        self.cli_name = cli_name

    def __str__(self) -> str:
        return f"Declared Generic Cli returned error on registering cli. GenericCLI is not subclass of {self.cli_name}"


class IncorrectCommandArgument(Exception):
    def __init__(self, command_name: str, attribute_value: str) -> None:
        self.command_name = command_name
        self.inc_attr_value = attribute_value

    def __str__(self) -> str:
        cprint(f"""
[bold red]Usage:[/bold red]
    [bold green]{self.command_name}[/bold green] [bold red]{self.inc_attr_value}[/bold red] [VALUE]
""")
        return f"Incorrect command argument. Command '{self.command_name}' has no attribute for {self.inc_attr_value}"
