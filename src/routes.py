from typing import Sequence
from ascender.core.router.interface.route import RouterRoute
from controllers.main_controller import MainController
from controllers.test.test_module import TestModule


routes: Sequence[RouterRoute] = [
    {
        "path": "/",
        "controller": MainController,
        "tags": ["Main Controller"],
        "include_in_schema": True
    },
    {
        "path": "/test",
        "load_controller": lambda: TestModule,
        "tags": ["Test Controller"],
        "include_in_schema": True
    }
]

__all__ = ["routes"]
