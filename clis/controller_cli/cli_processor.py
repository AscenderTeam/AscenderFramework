from clis.controller_cli.controller_creator import ControllerCreator
from core.cli import GenericCLI
from core.cli.main import console_command
from core.cli.application import ContextApplication

class ControllerCLI(GenericCLI):
    app_name: str = "controllers"
    help: str = "Easily manage controllers with this CLI tool"

    def __init__(self) -> None:
        self._name = "ControllerCLI"
        self._description = "Easily manage controllers with this CLI tool"
        self._version = "0.0.1"

    @console_command
    def new(self, ctx: ContextApplication, name: str, cname: str = "controllers"):
        ctx.console_print(f"[cyan]Creating new controller with name:[/cyan] {name}...")
        ctx.console_print("[yellow]Warning![/yellow] Avoid passing the controller name with spaces!")
        controller_creator = ControllerCreator(name, cname)
        
        for controller in controller_creator.create_controller():
            ctx.console_print(f"[green]Created file:[/green] {name}/{controller}")

        ctx.console_print(f"[cyan]Done! You can check it up in: [underline]{controller_creator.controller_constants.controllers_path}/{controller_creator.controller_constants.controller_name.lower()}[/underline][/cyan]")
    
    @console_command
    def optionals(self, ctx: ContextApplication, name: str, cname: str = "controllers"):
        ctx.console_print(f"[cyan]Adding optional files to controller with name:[/cyan] {name}...")
        ctx.console_print("[yellow]Warning![/yellow] Avoid passing the controller name with spaces!")
        controller_creator = ControllerCreator(name, cname)
        
        for controller in controller_creator.create_optional_files():
            ctx.console_print(f"[green]Created file:[/green] {name}/{controller}")

        ctx.console_print(f"[cyan]Done! You can check it up in: [underline]{controller_creator.controller_constants.controllers_path}/{controller_creator.controller_constants.controller_name.lower()}[/underline][/cyan]")