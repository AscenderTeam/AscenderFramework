import os
import subprocess
import sys
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import BaseCLI
from ascender.core.cli.models import ArgumentCMD


class RunCLI(BaseCLI):
    _config = {"ignore_unknown_options": True, "allow_extra_args": True}

    def __init__(self):
        ...
    
    def callback(
        self, 
        ctx: ContextApplication
    ):
        os.environ["CLI_MODE"] = "0"
        return subprocess.call(f"poetry run python start.py {' '.join(sys.argv[2:])}", shell=True)