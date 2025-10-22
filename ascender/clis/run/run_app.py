from argparse import REMAINDER
import os
import random
import subprocess
import sys
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.cli.application import ContextApplication
from ascender.core.cli_engine import Command, BasicCLI, Parameter

from rich import print as rprint


@Command(name="run", description="Run the Ascender Framework application.", aliases=["r"], help="Lunch the Ascender Framework application including custom CLI commands.", add_help=False)
class RunCLI(BasicCLI):
    
    extra: list[str] = Parameter(default_factory=list, names=["extra"], description="Additional arguments to pass to the application.", nargs=REMAINDER)

    def __init__(self):
        ...

    def execute(self):
        os.environ["CLI_MODE"] = "0"
        
        if "relax" in self.extra: return self.get_cow()
        source = _AscenderConfig().config.paths.source
        try:
            return subprocess.call(f"poetry run python {source}/main.py {' '.join(self.extra)}", shell=True)
        except KeyboardInterrupt:
            rprint("\n[yellow]Exiting ascender run mode...[/yellow]")
            rprint("\n[cyan]Gracefully shutting down the Ascender application...[/cyan]")

    def get_cow(self):
        relax_replicas = [
            "Take a deep breath. The bugs will fix themselves... maybe.",
            "Debugging is like being the detective in a crime movie where you are also the murderer.",
            "Code never lies... unless it's yours.",
            "Let the coffee flow, and the bugs disappear.",
            "Relax, the compiler is just having a bad day.",
            "Everything will be okay. If not, there's always Stack Overflow.",
            "Remember: It works on your machine, and that's all that matters.",
            "Keep calm and blame the intern.",
        ]
        cow = r"""
 ______
< Relax >
 ------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""
        rprint(f"\"{random.choice(relax_replicas)}\"\n{cow}")