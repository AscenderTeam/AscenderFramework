from typing import Literal

import click
from ascender.clis.generator.create_generator_service import CreateGeneratorService
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import GenericCLI, console_command
from ascender.core.cli.models import ArgumentCMD, OptionCMD
from ascender.core.database.types.orm_enum import ORMEnum


class GeneratorCLI(GenericCLI):
    app_name: str = "generate"
    help: str = "Generates service|controller|guard|cli|module"

    def __init__(
        self,
        create_generator_service: CreateGeneratorService
    ):
        self.create_generator_service = create_generator_service

    @console_command(name="controller")
    def generate_controller(
        self,
        ctx: ContextApplication,
        name: str,
        standalone: bool = OptionCMD("--no-standalone", default=False, is_flag=True, required=False),
        prefix: str = OptionCMD("-p", default="", required=False),
        suffix: str = OptionCMD("-s", default="", required=False),
        module: str | None = OptionCMD(
            "-m", default=None, ctype=str, required=False),
    ):
        if name == "unicorn":
            ctx.console_print("Generating unicorn... 🦄")
            ctx.console_print("[red]Error:[/] Unicorns are mythical. Try generating a 'real' controller instead.")
            return
        
        module_update, file_info = self.create_generator_service.generate_controller(
            name, standalone,
            prefix, suffix,
            module
        )
        ctx.console_print(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if module_update:
            ctx.console_print(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")
    
    @console_command(name="service")
    def generate_service(
        self,
        ctx: ContextApplication,
        name: str,
        module: str | None = OptionCMD(
            "-m", default=None, ctype=str, required=False),
    ):
        module_update, file_info = self.create_generator_service.generate_service(name, module)
        ctx.console_print(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if module_update:
            ctx.console_print(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")
    
    @console_command(name="module")
    def generate_module(
        self,
        ctx: ContextApplication,
        name: str,
        module: str | None = OptionCMD("-m", default=None, ctype=str, required=False)
    ):
        module_update, file_info = self.create_generator_service.generate_module(name, module)
        ctx.console_print(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")

        if module_update:
            ctx.console_print(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")

    @console_command(name="repository")
    def generate_repository(
        self,
        ctx: ContextApplication,
        name: str,
        entities: list[str] = OptionCMD("-e", multiple=True, ctype=str),
        orm_mode: str = OptionCMD("--orm", "-om", ctype=click.Choice([e.value for e in ORMEnum])),
        module: str | None = OptionCMD("-m", default=None, ctype=str, required=False)
    ):
        repository = self.create_generator_service.generate_repository(
            name, 
            entities=entities, 
            orm_mode=ORMEnum(orm_mode), 
            module=module
        )
        if isinstance(repository, dict):
            return ctx.console_print(f"[yellow]{repository['schematic_type']}[/yellow] {repository['file_path']} [cyan]({repository['write_size']} bytes)[/cyan]")

        module_update, file_info = repository
        ctx.console_print(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if module_update:
            ctx.console_print(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")
    
    @console_command(name="guard")
    def generate_guard(
        self,
        ctx: ContextApplication,
        name: str,
        guard_type: Literal["single", "parametrized"] = OptionCMD("--guard-type", "-gt", 
                                                                  ctype=click.Choice(["single", "parametrized"]), default="single", required=False),
        guards: list[str] = OptionCMD("--guards", required=False, multiple=True),
        module: str | None = OptionCMD("-m", default=None, ctype=str, required=False)
    ):
        guard_update, file_info = self.create_generator_service.generate_guard(
            name, guard_type, guards, module
        )
        
        ctx.console_print(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if guard_update:
            ctx.console_print(f"[yellow]{guard_update['schematic_type']}[/yellow] {guard_update['file_path']} [cyan]({guard_update['write_size']} bytes)[/cyan]")
