"""
### Ascender Framework

A simple and powerful Web API framework for python. Developed by [Ascender](https://ascender.space)
"""
import os
from ascender.core.application import Application
from ascender.core.types import Controller, IBootstrap


def ascender_launcher(
        main_controller: Controller,
        configuration: IBootstrap
    ):

    app = Application(main_controller, configuration)

    return app


def _builtin_launcher():
    os.environ["CLI_MODE"] = "1"
    
    return Application(object, {}).run_cli()
