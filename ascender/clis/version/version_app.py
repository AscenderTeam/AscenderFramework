from __future__ import annotations
from ascender.core.cli_engine import Command, BasicCLI, BooleanParameter

import platform
import subprocess
import sys

# Try to get the Ascender package version: prefer ascender.__version__ if available,
# otherwise use importlib.metadata (or the backport importlib_metadata) and finally fall back.
try:
    from ascender import __version__ as ASCENDER_VERSION # type: ignore
except Exception:
    try:
        from importlib.metadata import version as _get_version
    except Exception:
        try:
            # Backport for older Python versions
            from importlib_metadata import version as _get_version  # type: ignore
        except Exception:
            _get_version = lambda name: "Unknown"  # type: ignore

    try:
        ASCENDER_VERSION = _get_version("ascender")
    except Exception:
        ASCENDER_VERSION = "Unknown"

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


@Command("version", description="Display the Ascender Framework version and environment info")
class VersionCLI(BasicCLI):
    """
    Displays environment information such as Python, Poetry, OS, and Ascender Framework versions.
    """

    beautify: bool = BooleanParameter(flags=["--raw"], default=True, description="Whether to display formatted output using Rich")

    def __init__(self) -> None:
        super().__init__()
    def _get_system_info(self) -> dict[str, str]:
        """
        Collects system information without formatting (for logs or non-interactive environments).
        """
        try:
            poetry_version = (
                subprocess.check_output(["poetry", "--version"], text=True)
                .strip()
                .replace("Poetry (version ", "")
                .replace(")", "")
            )
        except Exception:
            poetry_version = "Unavailable"

        return {
            "Python Version": platform.python_version(),
            "Poetry Version": poetry_version,
            "Ascender Framework Version": ASCENDER_VERSION,
            "Operating System": f"{platform.system()} {platform.release()} ({platform.machine()})",
            "Implementation": platform.python_implementation(),
        }

    def _print_system_info_rich(self, info: dict[str, str]) -> None:
        """
        Prints system information using Rich for visually formatted output.
        """
        console = Console()
        title = Text("Ascender Framework Environment", style="bold cyan")

        table = Table(show_header=False, box=None, expand=False)
        for key, value in info.items():
            table.add_row(f"[bold white]{key}[/bold white]", f"[green]{value}[/green]")

        panel = Panel(
            table,
            border_style="cyan",
            title="[bold bright_white]System Info[/bold bright_white]",
            padding=(1, 2),
        )

        console.print(title)
        console.print(panel)
    
    def _print_system_info_plain(self, info: dict[str, str]) -> None:
        """
        Prints system information in plain text format.
        """
        for key, value in info.items():
            print(f"{key}: {value}")
            

    def execute(self) -> None:
        info = self._get_system_info()
        
        if self.beautify:
            self._print_system_info_rich(info)
        else:
            self._print_system_info_plain(info)
