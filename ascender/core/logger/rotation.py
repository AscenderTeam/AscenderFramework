from logging import FileHandler
import logging
from logging.handlers import RotatingFileHandler
import os

from ascender.core._config.interface.runtime import LoggingRotationConfig


def configure_file_logging(file: str, rotation: LoggingRotationConfig):
    """
    Configures a file handler with optional rotation.

    :param file: Path to the log file.
    :param rotation: Rotation configuration as a dictionary.
    :return: Configured file handler.
    """
    os.makedirs(os.path.dirname(file), exist_ok=True)
    if rotation.enabled:
        max_size = int(rotation.max_size.rstrip("MB")) * 1024 * 1024
        file_handler = RotatingFileHandler(file, maxBytes=max_size, backupCount=rotation.backup_count)
    else:
        file_handler = FileHandler(file, mode="a", encoding="utf-8")
    
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    ))
    return file_handler