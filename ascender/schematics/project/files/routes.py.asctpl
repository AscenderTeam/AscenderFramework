from typing import Sequence
from ascender.core.router import RouterRoute
from controllers.main_controller import MainController


routes: Sequence[RouterRoute] = [
    {
        "path": "/",
        "controller": MainController,
        "tags": ["Main Controller"],
        "include_in_schema": True
    },
]

__all__ = ["routes"]