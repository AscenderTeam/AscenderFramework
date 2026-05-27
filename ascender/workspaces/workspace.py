import os
from typing import Sequence

from pydantic import ValidationError

from ascender.core.cli_engine import BasicCLI, CLIEngine, Command, GenericCLI
from ascender.workspaces._configs.workspace import WorkspaceConfigs
from ascender.workspaces.scripts.scripts import ScriptsCLI


class Workspace:
    def __init__(
        self,
        configs: os.PathLike | str,
        cli_usage: str | None = None,
    ) -> None:
        self._configs = configs

        if isinstance(configs, str):
            self._configs = os.path.abspath(configs)

        self.workspace_configs = self.load_configs()
        self.cli = CLIEngine(usage=cli_usage)

    def load_configs(self):
        try:
            configs = WorkspaceConfigs.model_validate_json(open(self._configs).read())
        except OSError as e:
            # TODO: Add custom error
            raise e

        except ValidationError as e:
            # TODO: Add custom error
            raise e

        return configs

    def add_cli(self, commands: Sequence[BasicCLI | GenericCLI]) -> None:
        self.cli.process_commands(commands)

    def run(self):
        script_commands = []

        for script in self.workspace_configs.scripts:
            script_cls = type(f"ScriptsCLI_{script.name}", (ScriptsCLI,), {})
            cli = Command(name=script.name)(script_cls)()
            cli.set_command(script.command, cwd=script.cwd)  # pyright: ignore[]
            script_commands.append(cli)

        self.cli.process_commands(script_commands)

        self.cli()
