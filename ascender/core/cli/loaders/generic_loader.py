from __future__ import annotations
from inspect import unwrap
from typing import TYPE_CHECKING, Callable, Optional

import rich_click as click
from rich_click import RichCommand, RichGroup
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import GenericCLI
from ascender.core.cli.models import ArgumentCMD, ArgumentsFormat

if TYPE_CHECKING:
    from ascender.core.applications.application import Application


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
            method = getattr(self.cli, name)
            method(ctx=ctx, **kwargs)
        
        return call_cli

    def _as_command(self, name: str, method_name: str, arguments: list[ArgumentsFormat], **metadata) -> None:
        command = RichCommand(name, context_settings=self.cli.configs, callback=self.execute_cli(method_name), **metadata)
        
        for arg in arguments:
            if arg["is_ourobj"]:
                if arg["type"] == ArgumentCMD:
                    command.params.append(click.Argument([arg["argument"]], type=arg["value"].type, default=arg["value"].default, required=(arg["value"].required)
                                                 ))
                else:
                    command.params.append(arg["value"].parse(arg["argument"]))

                continue
                    
            command.params.append(click.Argument([arg["argument"]], type=arg["type"], default=arg["value"], required=(arg["value"] is None)
                                                 ))
        
        return command


    def _as_group(self) -> RichGroup:
        methods = self.cli.get_methods()
        group = RichGroup(name=self.name)
        for name, arguments in methods:
            
            try:
                method_meta = getattr(self.cli, name)
                command = self._as_command(method_meta.alt_name or name, method_name=name, arguments=arguments, help=method_meta.help, **method_meta.kwargs)
                group.add_command(command)

            except AttributeError:
                continue
        # Run group
        return group

    def run(self) -> RichGroup:
        group = self._as_group()
        return group

    def __call__(self) -> None:
        self.run()