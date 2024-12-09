from typing import TypeVar

from inflection import titleize

from ascender.abstracts.module import AbstractModule
from ascender.common import inject
from ascender.core.application import Application
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case


ModuleOrController = TypeVar("ModuleOrController")
Controller = TypeVar("Controller")


class ProvideControllers(AbstractModule):
    application: Application

    def __init__(
        self,
        controllers: list[ModuleOrController]
    ):
        self.controllers = controllers

    async def on_application_bootstrap(self, application: Application):
        self.application = application
        await self.load_controllers()

    async def load_controllers(self):
        for controller in self.controllers:
            if hasattr(controller, "__declaration_type__") and hasattr(controller, "router"):
                controller = self.handle_standalone_controller(controller)
                await self.load_controller(controller)
                continue

            if hasattr(controller, "asc_module") and hasattr(controller, "bootstrap"):
                await self.handle_module(controller)
                continue
    
    async def load_controller(self, controller: Controller, _use_name_prefix: bool = True):
        controller.load_routes(controller.router)
        await controller.on_application_bootstrap(application=self.application)

        _url_prefix = ""
        
        if _use_name_prefix:
            if controller._router_name:
                _url_prefix = controller._router_name
            else:
                _url_prefix = kebab_case(controller.__class__.__name__.removesuffix("Controller"))


        self.application.app.include_router(
            controller.router, 
            prefix=f"{controller._router_prefix}/{_url_prefix}",
            tags=[titleize(pascal_case(_url_prefix))]
        )

    def handle_standalone_controller(self, controller: type[Controller]):
        controller = controller.bootstrap(controller)

        return controller

    async def handle_module(self, module: ModuleOrController):
        # Initialize module
        module = module()

        # Initialize module's DI
        module.bootstrap()

        # Load all controllers of the module
        module_scopes: dict[type[ModuleOrController], ModuleOrController] = module._module_scope
        
        for scope_type, scope_item in module_scopes.items():
            if hasattr(scope_type, "__declaration_type__"):
                await self.load_controller(scope_item)
        
        await module.on_application_bootstrap(self.application)