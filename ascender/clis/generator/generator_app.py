from typing import Literal

from ascender.clis.generator.create_generator_service import CreateGeneratorService
from ascender.core.cli_engine import Command, Handler, BooleanParameter, Parameter, GenericCLI
from ascender.core.database.types.orm_enum import ORMEnum

from rich import print as rprint


@Command(name="generate", description="Generate application components like controllers, services, modules, repositories, and guards.", aliases=["g"], help="Generate various project components.")
class GeneratorCLI(GenericCLI):

    def __init__(
        self,
        create_generator_service: CreateGeneratorService
    ):
        self.create_generator_service = create_generator_service

    @Handler("controller", "c", description="Generate a new controller. Alias: `c`.")
    def generate_controller(
        self,
        name: str,
        standalone: bool = BooleanParameter(False, description="Generate as a standalone controller", flags=["--standalone", "-s"]),
        prefix: str = Parameter("", names=["-pre", "--prefix"], description="Prefix for the controller name"),
        suffix: str = Parameter("", names=["-suf", "--suffix"], description="Suffix for the controller name"),
        module: str | None = Parameter(None, names=["-m", "--module"], description="Module to generate the controller in"),
    ):
        if name == "unicorn":
            rprint("Generating unicorn... 🦄")
            rprint("[red]Error:[/] Unicorns are mythical. Try generating a 'real' controller instead.")
            return
        
        module_update, file_info = self.create_generator_service.generate_controller(
            name, standalone,
            prefix, suffix,
            module
        )
        rprint(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if module_update:
            rprint(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")

    @Handler("service", "s", description="Generate a new service. Alias: `s`.")
    def generate_service(
        self,
        name: str,
        module: str | None = Parameter(default=None, names=["-m", "--module"], description="Module to generate the service in"),
    ):
        module_update, file_info = self.create_generator_service.generate_service(name, module)
        rprint(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if module_update:
            rprint(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")

    @Handler("module", "m", description="Generate a new module. Alias: `m`.")
    def generate_module(
        self,
        name: str,
        module: str | None = Parameter(default=None, names=["-m", "--module"], description="Module to generate the module in"),
    ):
        module_update, file_info = self.create_generator_service.generate_module(name, module)
        rprint(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")

        if module_update:
            rprint(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")

    @Handler("repository", "r", description="Generate a new repository. Alias: `r`.")
    def generate_repository(
        self,
        name: str,
        entities: tuple[str] | None = Parameter(None, names=["-e", "--entities"], description="List of entities to include in the repository", nargs="*"),
        orm_mode: str = Parameter("default", names=["--orm-mode"], description="ORM mode to use for the repository"),
        module: str | None = Parameter(default=None, names=["-m", "--module"], description="Module to generate the repository in")
    ):
        repository = self.create_generator_service.generate_repository(
            name, 
            entities=entities or tuple(), 
            orm_mode=ORMEnum(orm_mode), 
            module=module
        )
        if isinstance(repository, dict):
            return rprint(f"[yellow]{repository['schematic_type']}[/yellow] {repository['file_path']} [cyan]({repository['write_size']} bytes)[/cyan]")

        module_update, file_info = repository
        rprint(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if module_update:
            rprint(f"[yellow]{module_update['schematic_type']}[/yellow] {module_update['file_path']} [cyan]({module_update['write_size']} bytes)[/cyan]")

    @Handler("guard", "gd", description="Generate a new guard. Alias: `gd`.")
    def generate_guard(
        self,
        name: str,
        guard_type: Literal["single", "parametrized"] = Parameter("single", names=["--type"], description="Type of guard to generate"),
        module: str | None = Parameter(default=None, names=["-m", "--module"], description="Module to generate the guard in"),
        guards: tuple[str] | None = Parameter(None, names=["--guards"], description="List of guards to include", nargs="+", action="extend")
    ):
        guard_update, file_info = self.create_generator_service.generate_guard(
            name, guard_type, guards, module
        )
        
        rprint(f"[green]{file_info['schematic_type']}[/green] {file_info['file_path']} [cyan]({file_info['write_size']} bytes)[/cyan]")
        if guard_update:
            rprint(f"[yellow]{guard_update['schematic_type']}[/yellow] {guard_update['file_path']} [cyan]({guard_update['write_size']} bytes)[/cyan]")