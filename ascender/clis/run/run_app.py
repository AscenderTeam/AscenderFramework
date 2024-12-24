import subprocess
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import BaseCLI
from ascender.core.cli.models import ArgumentCMD


class RunCLI(BaseCLI):
    command: str = ArgumentCMD(nargs=-1)

    def __init__(self):
        ...
    
    def callback(
        self, 
        ctx: ContextApplication
    ):
        ctx.console_print(self.command)
        return subprocess.call(f"poetry run python start.py {self.command}")