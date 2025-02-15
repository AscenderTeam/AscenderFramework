from logging import getLogger
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ascender.core._config.asc_config import _AscenderConfig


def configure_staticfile_serving(app: FastAPI):
    config = _AscenderConfig().config

    if config.features.staticFileServing:
        path = os.path.abspath(config.paths.static)
        os.makedirs(path, exist_ok=True)
        
        # logger.debug(f"Mounting statics directory in {path}")

        app.mount("/static", StaticFiles(directory=path), name="static")
        # logger.info("Successfully mounted statics dir")