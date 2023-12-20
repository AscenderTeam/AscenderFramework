from rich.prompt import Prompt, Confirm

from clis.controller_cli.controller_creator import ControllerCreator
from core.cli import GenericCLI
from core.cli.main import console_command
from core.cli.application import ContextApplication


class ControllerCLI(GenericCLI):
    app_name: str = "ControllerCLI"
    help: str = "🔧 Easily manage controllers with this CLI tool"

    def __init__(self) -> None:
        self._name = "ControllerCLI"
        self._description = "🔧 Easily manage controllers with this CLI tool"
        self._version = "0.0.1"

    @console_command
    def new_controller(self, ctx: ContextApplication):
        ctx.console_print("🚀 [bold cyan]Create a new controller[/bold cyan]")
        controller_name = Prompt.ask("Controller name", default="auto")
        include_optionals = Confirm.ask("Include optionals", default=True)
        description_prompt = Prompt.ask("Controller description prompt", default=None)

        controller_creator = ControllerCreator(controller_name)
        if controller_name == 'auto' and description_prompt:  # if user needs a name
            ctx.console_print(f"[cyan]Creating new controller with name: ", end='', flush=True)
            controller_name = controller_creator.generate_name(description=description_prompt)
            ctx.console_print(f'[bold]{controller_name}[/bold]... 🛠')

        if description_prompt:
            for controller_file in controller_creator.generate_controller(description_prompt, controller_name):
                try:
                    ctx.console_print(f"[bright_black]{controller_file[1][200:400]}...[/bright_black]")
                except IndexError:
                    ctx.console_print(f"[bright_black]{controller_file[1][:200]}...[/bright_black]")
                ctx.console_print(f"[green]✅ Created file:[/green] {controller_name}/{controller_file[0]}")
            ctx.console_print(
                f"🎉 [cyan]All set! Check your new controller at: [underline]{controller_creator.controller_constants.controllers_path}/{controller_creator.controller_constants.controller_name.lower()}[/underline][/cyan]")
            return

        created_files = controller_creator.create_controller()
        for file in created_files:
            ctx.console_print(f"[green]✅ Created file:[/green] {controller_name}/{file}")
        if include_optionals:
            for controller in controller_creator.create_optional_files():
                ctx.console_print(f"[green]Created additional file:[/green] {controller_name}/{controller}")
        ctx.console_print(
            f"🎉 [cyan]All set! Check your new controller at: [underline]{controller_creator.controller_constants.controllers_path}/{controller_creator.controller_constants.controller_name.lower()}[/underline][/cyan]")
