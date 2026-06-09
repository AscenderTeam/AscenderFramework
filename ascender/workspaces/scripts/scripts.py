import os
import subprocess

from rich import print

from ascender.core.cli_engine import BasicCLI


class ScriptsCLI(BasicCLI):
    _command: str | list[str]
    _cwd: str

    def set_command(self, command: str | list[str], cwd: str | None = None):
        self._command = command
        self._cwd = cwd if cwd is not None else os.getcwd()

    def execute(self) -> None:
        if hasattr(self, "_command"):
            subprocess.call(
                self._command if isinstance(self._command, list) else [self._command],
                cwd=os.path.abspath(self._cwd),
                shell=True,
            )
        else:
            print("[bold red]No command provided[/]")
