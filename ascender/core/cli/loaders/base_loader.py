from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

import rich_click as click
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import BaseCLI
from ascender.core.cli.models import ArgumentCMD, CommandNull, OptionCMD

if TYPE_CHECKING:
    from ascender.core.application import Application


class LoaderBaseCLI:
    def __init__(self, cli: BaseCLI, application: Application,
                 name: str,
                 callback: Optional[Callable[[ContextApplication], None]] = None) -> None:
        self.application = application
        self.callback = callback
        self.name = name
        self.cli = cli
    
    def get_arguments(self):
        arguments = self.cli.get_arguments()

        for index, argument in enumerate(arguments):
            if argument["argument"] == "ctx":
                del arguments[index]
            
            if argument["is_ourobj"]:
                arguments[index] = {
                    "argument": argument["argument"] if not isinstance(argument["value"], ArgumentCMD) or not argument["value"].name else argument["value"].name,
                    "type": argument["value"].type if argument["value"].type is not None else argument["type"],
                    "value": argument["value"],
                    "help": argument["value"].help,
                    "is_arg": type(argument["value"]) == ArgumentCMD,
                    "is_ourobj": True,
                }
            else:
                arguments[index] = {
                    "argument": argument["argument"],
                    "type": argument["type"],
                    "value": argument["value"],
                    "is_arg": type(argument["value"]) == ArgumentCMD,
                    "is_ourobj": False,
                }
        return arguments
    
    def execute_cli(self, **kwargs):
        ctx = ContextApplication(self.application)
        for key, value in kwargs.items():
            setattr(self.cli, key, value)

        return self.cli.callback(ctx=ctx)

    def _as_command(self) -> None:
        arguments = self.get_arguments()
        command = click.RichCommand(self.name, context_settings=self.cli._config, callback=self.execute_cli)
        
        for arg in arguments:
            if arg["is_ourobj"]:
                if arg["is_arg"]:
                    command.params.append(click.Argument([arg["argument"]], type=arg["type"], default=arg["value"].default, required=arg["value"].required, **arg["value"].additional_kwargs
                                                 ))
                else:
                    command.params.append(arg["value"].parse(arg["argument"]))
                # Skip the loop without reaching what's written lower
                continue

            command.params.append(click.Argument([arg["argument"]], type=arg["type"], default=arg["value"], required=(arg["value"] is None)
                                                 ))
        
        return command
    
    def run(self) -> click.RichCommand:
        command = self._as_command()

        return command