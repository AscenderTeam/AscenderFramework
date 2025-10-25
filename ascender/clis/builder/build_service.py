import os
from ascender.clis.builder.build_message_service import BuildMessageService
from ascender.core import Service
from ascender.common import Injectable
from ascender.core._builder.file_builder import build_file_manager
from ascender.core._builder.minifier import minify_project
from ascender.core._builder.obfuscator import obfuscate_project
from ascender.core._config.asc_config import _AscenderConfig
from rich import print as rprint


@Injectable(provided_in="root")
class BuildService(Service):
    def __init__(self, build_message_service: BuildMessageService):
        self.build_message_service = build_message_service

    def get_configs(self):
        os.environ["ASC_MODE"] = "build"
        os.environ["CLI_MODE"] = "0"
        return _AscenderConfig().config

    def start_build(self):
        configs = self.get_configs()
        build_configs = configs.build

        # display start message using rich print
        rprint(f"[green]INFO[/green] Building {configs.project['name']} - Ascender Framework Project")
        rprint("[cyan]Preparing configuration files for build[/cyan]")

        if build_configs.obfuscate:
            rprint("[green]INFO[/] [yellow]`Obfuscation` detected in `ascender.json`[/]")
            rprint("[green]INFO[/] Using [cyan bold]PyInstaller[/] to build project...")
            rprint("[green]INFO[/] Using [cyan bold]PyInstaller[/] to build project...")
            self.build_file_manager(False)

            obfuscate_project(
                configs.project["name"], configs.paths.output, configs.paths.source, configs.build.packages, configs.build.importMetadata
            )

            rprint("[green]INFO[/] [cyan]Obfuscation finished, build has been completed...[cyan]")
            rprint(f"[green]INFO[/] [cyan]Build distribution is available in {configs.paths.output}/{configs.project['name']}[cyan]")
            # display_obfuscated_instructions had no implementation in the message service, skipping.
            return

        if build_configs.minify:
            rprint("[green]INFO[/] [yellow]`minify` detected in `ascender.json`[/]")
            rprint("[green]INFO[/] Using [cyan bold]python-minifier[/] to build project...")
            rprint("[green]INFO[/] Using [cyan bold]python-minifier[/] to build project...")
            self.build_file_manager(False)
            minify_project(
                configs.project["name"], 
                configs.paths.output, 
                configs.paths.source, 
                build_configs.stripComments
            )
            rprint("[green]INFO[/] [cyan]Minification finished, build has been completed...[cyan]")
            rprint(f"[green]INFO[/] [cyan]Build distribution is available in {configs.paths.output}/{configs.project['name']}[cyan]")
            return
        
        self.build_file_manager(True)
        rprint(f"[yellow]Classic build has been finished, check out {configs.paths.output}/{configs.project['name']}...[/]")

    def build_file_manager(self, use_source: bool = True):
        configs = self.get_configs()
        build_configs = configs.build

        return build_file_manager(
            configs.project["name"], configs.paths.output, configs.project.get(
                "version", "0.1.0"
            ),
            None if not use_source else configs.paths.source,
            configs.paths.static if build_configs.includeStatic else None
        )
