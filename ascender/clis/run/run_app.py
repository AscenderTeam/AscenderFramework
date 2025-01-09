import os
import random
import subprocess
import sys
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import BaseCLI


class RunCLI(BaseCLI):
    _config = {"ignore_unknown_options": True, "allow_extra_args": True}

    def __init__(self):
        ...

    def callback(
        self,
        ctx: ContextApplication
    ):
        os.environ["CLI_MODE"] = "0"
        
        if " ".join(sys.argv).find("run relax") != -1: return self.get_cow(ctx)
        source = _AscenderConfig().config.paths.source
        return subprocess.call(f"poetry run python {source}/main.py {' '.join(sys.argv[2:])}", shell=True)

    def get_cow(
        self,
        ctx: ContextApplication
    ):
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
        ctx.console_print(f"\"{random.choice(relax_replicas)}\"\n{cow}")