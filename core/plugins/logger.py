import logging

class PluginsLoggerFormatter(logging.Formatter):
    """ Custom formatter to apply color based on the log level. """

    level_to_color = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red"
    }

    def format(self, record):
        levelname = record.levelname
        color = self.level_to_color.get(levelname, "white")
        formatted = "[bold cyan]Asc Plugin[/bold cyan] [{color}]{levelname}[/{color}]: {message}".format(
            color=color, levelname=levelname, message=record.getMessage()
        )
        return formatted
