from ascender.core.cli.application import ContextApplication
from ascender.core.cli.injectable import Injectable
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.core.registries.service import ServiceRegistry


class ControllerService(Injectable):
    def __init__(self, service_registry: ServiceRegistry) -> None:
        self._sr = service_registry

    def build_basic_controller(self, ctx: ContextApplication,
                               controller_name: str,
                               controller_path: str):
        ctx.console_print(f"[cyan]Creating new controller with name:[/cyan] {controller_name}...")
        
        # imported on row
        from .builders.basic import BasicBuilder

        builder = BasicBuilder(controller_name, controller_path)
        _controller = builder()

        ctx.console_print("[yellow]Warning![/yellow] Avoid passing the controller name with spaces and follow casing types!")
        
        for item in _controller:
            if item["type"] == "file":
                ctx.console_print(f"[green]Created file:[/green] {controller_path}/{controller_path}/{item['filename']}")
            else:
                ctx.console_print(f"[yellow]Created directory:[/yellow] {controller_path}/{controller_path}/{item['dirname']}")
            
        ctx.console_print(f"[cyan]Done! You can check it up in: [underline]{builder.controller_dir}/{controller_name.lower().replace(' ', '')}[/underline][/cyan]")
    
    def build_auth_controller(self, ctx: ContextApplication,
                              controller_name: str,
                              controller_path: str,
                              orm_mode: ORMEnum,
                              entity_module: str):
        ctx.console_print(f"[cyan]Creating new Identity Controller with name:[/cyan] {controller_name}...")
        
        # imported on row
        from .builders.auth import AuthBuilder

        builder = AuthBuilder(controller_name, controller_path, orm_mode, entity_module)
        _controller = builder()

        ctx.console_print("[yellow]Warning![/yellow] Avoid passing the controller name with spaces and follow casing types!")
        
        for item in _controller:
            if item["type"] == "file":
                ctx.console_print(f"[green]Created file:[/green] {controller_path}/{controller_path}/{item['filename']}")
            else:
                ctx.console_print(f"[yellow]Created directory:[/yellow] {controller_path}/{controller_path}/{item['dirname']}")
            
        ctx.console_print(f"[cyan]Done! You can check it up in: [underline]{builder.controller_dir}/{controller_name.lower().replace(' ', '')}[/underline][/cyan]")