from ascender.core import Service
from ascender.common import Injectable
from ascender.core.cli.application import ContextApplication


@Injectable(provided_in="root")
class BuildMessageService(Service):
    def __init__(self):
        ...
    
    def display_start_message(self, ctx: ContextApplication, project_name: str):
        ctx.console_print(f"[green]INFO[/green] Building {project_name} - Ascender Framework Project")
        ctx.console_print(f"[cyan]Preparing configuration files for build[/cyan]")

    def display_finish_message(self, ctx: ContextApplication, output_dir: str):
        ctx.console_print(f"[yellow]Classic build has been finished, check out {output_dir}...[/]")

    def display_obfuscation_start(self, ctx: ContextApplication):
        ctx.console_print("[green]INFO[/] [yellow]`Obfuscation` detected in `ascender.json`[/]")
        ctx.console_print("[green]INFO[/] Using [cyan bold]PyInstaller[/] to build project...")
        ctx.console_print("[green]INFO[/] Using [cyan bold]PyInstaller[/] to build project...")

    def display_obfuscation_finished(self, ctx: ContextApplication, output_dir: str):
        ctx.console_print("[green]INFO[/] [cyan]Obfuscation finished, build has been completed...[cyan]")
        ctx.console_print(f"[green]INFO[/] [cyan]Build distribution is available in {output_dir}[cyan]")

    def display_obfuscated_instructions(self, ctx: ContextApplication):
        ...
    
    def display_minification_start(self, ctx: ContextApplication):
        ctx.console_print("[green]INFO[/] [yellow]`minify` detected in `ascender.json`[/]")
        ctx.console_print("[green]INFO[/] Using [cyan bold]python-minifier[/] to build project...")
        ctx.console_print("[green]INFO[/] Using [cyan bold]python-minifier[/] to build project...")

    def display_minification_finished(self, ctx: ContextApplication, output_dir: str):
        ctx.console_print("[green]INFO[/] [cyan]Minification finished, build has been completed...[cyan]")
        ctx.console_print(f"[green]INFO[/] [cyan]Build distribution is available in {output_dir}[cyan]")