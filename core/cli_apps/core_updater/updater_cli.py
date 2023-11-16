from time import sleep
from core.cli import GenericCLI
from core.cli.application import ContextApplication
from core.cli.main import console_command
from core.cli_apps.core_updater.console_embedder import ConsoleEmbedder
from core.cli_apps.core_updater.core_constants import CoreConstants

from rich.tree import Tree
from rich.progress import Progress


class UpdaterCLI(GenericCLI):
    
    def __init__(self) -> None:
        super().__init__()
        self.core_constants = CoreConstants()
        self.console_embedder = ConsoleEmbedder()

    @console_command
    def updater_core_dirs(self, ctx: ContextApplication):
        core_files = self.core_constants.scan_core_files()
        tree = Tree("CORE Direcotry Files", style="tree")
        
        self.console_embedder.embed_core_files(tree, core_files)
        ctx.console_print(tree)
    
    @console_command
    def compare_core_files(self, ctx: ContextApplication, strict: bool = False):
        with Progress() as progress:
            task1 = progress.add_task("[yellow]Preparing for scanning...", total=100)
            total_length_of_files = self.core_constants.length_of_core_files()[0]
            task2 = progress.add_task("[purple]Scanning... [cyan]", total=total_length_of_files + 5, scanning_file="core/")

            progress.update(task1, advance=10)

            for i, scan in enumerate(self.core_constants.compare_core_files()):
                progress.update(task2, description=f"[purple]Scanning[/purple] [cyan]{scan['name']}[/][purple]...[/]", advance=1, completed=i + 1)
                sleep(0.05)

            progress.update(task2, description=f"[green]Scanning completed! {total_length_of_files} were scanned", completed=total_length_of_files + 5)
            sleep(1.05)
            progress.stop()
            tree = Tree("CORE Direcotry Files Health Care", style="tree")
    
            self.console_embedder.embed_checked_files(tree, self.core_constants.checkup_result)
            ctx.console_print(tree)
            ctx.console_print(f"[cyan]Scanned {total_length_of_files} files![/cyan]")
            sleep(0.10)