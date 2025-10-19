import os
from typing import Any
from ascender.core.applications.application import Application


def build(app: Application, config: dict[str, Any]):
    """
    NOTE: Beta note, currently this feature is in beta testing

    Args:
        app (Application): Ascender Framework Application object
    """
    from uvicorn import run
    host = os.getenv("ASC_HOST", "127.0.0.1")
    port = os.getenv("ASC_PORT", "8000")
    run(app, host=host, port=int(port), **config)