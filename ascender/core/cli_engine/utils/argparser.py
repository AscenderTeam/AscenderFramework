from argparse import ArgumentParser
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class RichArgumentParser(ArgumentParser):
    """ArgumentParser that prints a rich-formatted error and shows help."""

    def error(self, message: str) -> None:
        console = Console()
        panel = Panel(Text(message, style="bold white on red"), title="Error", border_style="red")
        console.print(panel)
        console.print()
        try:
            self.print_help()
        except Exception:
            pass
        self.exit(2)