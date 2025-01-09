from logging import Logger, getLogger
from rich.logging import RichHandler
import logging
import os

from ascender.core._config.interface.environment import EnvironmentConfig
from ascender.core._config.interface.runtime import LoggingConfig, ServerConfig
from ascender.core.logger.formatter import AscenderFormatter

from .rotation import configure_file_logging


def configure_logger(config: LoggingConfig):
    """
    Configures a logger with the AscenderFormatter.
    
    :param name: Name of the logger.
    :param level: Logging level (default is DEBUG).
    :param log_file: Optional file path to write logs to.
    :return: Configured logger instance.
    """
    # Create logger
    logger = getLogger("Ascender Framework")

    logger.setLevel(config.level.upper())
    logger.propagate = False  # Avoid duplicate logs if root logger is configured

    rich_formatter = AscenderFormatter()

    # Create stream handler for console output
    if config.console:
        rich_handler = RichHandler(rich_tracebacks=True, markup=True)
        rich_handler.setFormatter(rich_formatter)
        logger.addHandler(rich_handler)

    # Optional: Create file handler for logging to a file
    if config.file:
        rotation_config = config.rotation
        file_handler = configure_file_logging(os.path.abspath(config.file), rotation_config)
        logger.addHandler(file_handler)

    return logger


def configure_uvicorn_logger(config: LoggingConfig, environment: EnvironmentConfig):
    """
    Configure Uvicorn-specific loggers to align with the application's logging setup.
    """
    uvicorn_access = getLogger("uvicorn.access")
    uvicorn_access.setLevel(environment.logging.upper())
    uvicorn_access.propagate = False

    # Add handlers to Uvicorn loggers
    formatter = AscenderFormatter()
    console_handler = RichHandler(show_time=False, show_path=False)
    console_handler.setFormatter(formatter)

    uvicorn_access.addHandler(console_handler)

    if config.file:
        rotation_config = config.rotation
        file_handler = configure_file_logging(os.path.abspath(config.file), rotation_config)
        uvicorn_access.addHandler(file_handler)
    
    return uvicorn_access