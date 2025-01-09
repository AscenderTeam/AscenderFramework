import logging
from typing import Any
from rich.console import Console
from rich.text import Text
from rich.logging import RichHandler


class AscenderFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        console = Console()
        
        # Extract log details
        timestamp = self.formatTime(record, "%H:%M:%S")
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()

        # Color-code log levels
        level_markup = {
            "DEBUG": "[cyan]DEBUG[/cyan]",
            "INFO": "[green]INFO[/green]",
            "WARNING": "[yellow]WARNING[/yellow]",
            "ERROR": "[red]ERROR[/red]",
            "CRITICAL": "[bold red]CRITICAL[/bold red]"
        }

        
        # Format log message
        markup_message = (
            f"[dim]{timestamp}[/dim] ┆ "
            f"{level_markup.get(level, level)} ┆ "
            f"[magenta]{logger_name}[/magenta] ┆ "
            f"{message}"
        )# Message content
        
        return markup_message