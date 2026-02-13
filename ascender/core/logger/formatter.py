import json
import logging
from datetime import datetime

from rich.console import Console


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
            "CRITICAL": "[bold red]CRITICAL[/bold red]",
        }

        # Format log message
        markup_message = (
            f"[dim]{timestamp}[/dim] ┆ "
            f"{level_markup.get(level, level)} ┆ "
            f"[magenta]{logger_name}[/magenta] ┆ "
            f"{message}"
        )  # Message content

        return markup_message


class JsonAscenderFormatter(logging.Formatter):
    def __init__(self, service: str | None = None):
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "severity": record.levelname,
            "service": self.service or record.name,
            "message": record.getMessage(),
        }

        reserved = set(vars(logging.LogRecord("", 0, "", 0, "", (), None)))
        for key, value in record.__dict__.items():
            if key not in reserved and key not in log_obj:
                log_obj[key] = value

        return json.dumps(log_obj)