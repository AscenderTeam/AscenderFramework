from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Optional

import rich_click as click
from rich_click import RichCommand, RichGroup
from core.cli.application import ContextApplication
from core.cli.main import GenericCLI
from core.cli.models import ArgumentCMD, ArgumentsFormat

if TYPE_CHECKING:
    from core.application import Application


class GenericLoader:
    def __init__(self, cli: GenericCLI, application: Application, *, 
                 name: Optional[str] = None, 
                 callback: Optional[Callable[[ContextApplication], None]] = None ) -> None:
        self.application = application
        self.callback = callback
        self.name = cli.app_name if cli.app_name else name
        self.cli = cli

    def execute_cli(self, name: str):
        """
        Executes given CLI command
        """
        ctx = ContextApplication(self.application)
        def call_cli(**kwargs):
            getattr(self.cli, name)(ctx=ctx, **kwargs)
        
        return call_cli

    def _as_command(self, name: str, arguments: list[ArgumentsFormat]) -> None:
        command = RichCommand(name, callback=self.execute_cli(name))
        
        for arg in arguments:
            if arg["is_ourobj"]:
                if arg["type"] == ArgumentCMD:
                    command.params.append(click.Argument([arg["argument"]], type=arg["value"].type, default=arg["value"].default, required=(arg["value"].required)
                                                 ))
                else:
                    command.params.append(click.Option([f"--{arg['argument']}", arg["argument"]], type=arg["value"].type, default=arg["value"].default, required=(arg["value"].required)
                                                 ))
                    print(arg['argument'], arg)
                continue
                    
            command.params.append(click.Argument([arg["argument"]], type=arg["type"], default=arg["value"], required=(arg["value"] is None)
                                                 ))
        
        return command


    def _as_group(self) -> RichGroup:
        methods = self.cli.get_methods()
        group = RichGroup(name=self.name)

        for name, arguments in methods:
            command = self._as_command(name, arguments)
            group.add_command(command)
        
        # Run group
        return group

    def run(self) -> RichGroup:
        group = self._as_group()
        return group

    def __call__(self) -> None:
        self.run()