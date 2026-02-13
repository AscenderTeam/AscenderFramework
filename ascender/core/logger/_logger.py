import logging
import os
from logging import getLogger

from rich.logging import RichHandler

from ascender.core._config.asc_config import _AscenderConfig
from ascender.core._config.interface.runtime import LoggingConfig
from ascender.core.logger.formatter import (AscenderFormatter,
                                            JsonAscenderFormatter)

from .rotation import configure_file_logging


def configure_logger(config: LoggingConfig):
    root_logger = getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.propagate = False

    logger = getLogger("Ascender Framework")
    logger.setLevel(config.level.upper())
    logger.propagate = False

    # Console handler
    if config.console:
        if config.console_format == "json":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(JsonAscenderFormatter())
            logger.addHandler(console_handler)
        else:
            rich_handler = RichHandler(rich_tracebacks=True, markup=True)
            rich_handler.setFormatter(AscenderFormatter())
            logger.addHandler(rich_handler)

    # File handler
    if config.file:
        rotation_config = config.rotation
        logs_path = _AscenderConfig().config.paths.logs
        file_handler = configure_file_logging(
            os.path.abspath(os.path.join(logs_path, config.file)), rotation_config
        )
        if config.file_format == "json":
            file_handler.setFormatter(JsonAscenderFormatter())
        else:
            file_handler.setFormatter(AscenderFormatter())
        logger.addHandler(file_handler)

    return logger


# def configure_uvicorn_logger(config: LoggingConfig, environment: EnvironmentConfig):
#     """
#     Configure Uvicorn-specific loggers to align with the application's logging setup.
#     """
#     uvicorn_access = getLogger("uvicorn.access")
#     # uvicorn_access.setLevel(environment.logging.upper())
#     # uvicorn_access.propagate = False

#     # # Add handlers to Uvicorn loggers
#     # formatter = AscenderFormatter()
#     # console_handler = RichHandler(show_time=False, show_path=False)
#     # console_handler.setFormatter(formatter)

#     # uvicorn_access.addHandler(console_handler)

#     # if config.file:
#     #     rotation_config = config.rotation
#     #     file_handler = configure_file_logging(os.path.abspath(config.file), rotation_config)
#     #     uvicorn_access.addHandler(file_handler)

#     return uvicorn_access