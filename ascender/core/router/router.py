from logging import getLogger
from typing import Sequence, cast

from fastapi import APIRouter
from ascender.core.applications.root_injector import RootInjector
from ascender.core.di.injector import AscenderInjector
from ascender.core.errors.not_standalone import NotStandaloneError
from ascender.core.router.interface.route import RouterRoute
from ascender.core.router.utils.controller import is_direct_controller, is_module_controller, unwrap_module_controller
from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.module import load_module


class RouterNode:
    controller: ControllerRef
    router: APIRouter
    children: list["RouterNode"]

    def __init__(self, route: RouterRoute, injector: AscenderInjector | None = None) -> None:
        self.injector = injector if injector else RootInjector().existing_injector

        self.logger = getLogger("Ascender Framework")
        self.route = route
        self.children = []

        self.router = APIRouter(
            prefix=route["path"].rstrip("/"), 
            tags=route.get("tags", []), # type: ignore
            include_in_schema=route.get("include_in_schema", False),
            deprecated=route.get("deprecated", False)
        )

        self.__process_children(route.get("children", []), self.injector)
        self.hydrate()
        self.load_routes()

    def __process_children(self, children: Sequence[RouterRoute], injector: AscenderInjector):
        """
        Processes child routes of current router and creates another router node in router graph

        Args:
            children (Sequence[RouterRoute]): Child elements of current router
        """
        for child_route in children:
            # Create another router node
            _node = RouterNode(child_route, injector)

            # Include it's router into our router
            self.router.include_router(_node.router)
            self.children.append(_node)
    
    def __load_children(self, module: type[AscModuleRef]):
        """
        Loads routes from module and attaches them to this route as `children`

        Args:
            module: Module to load routes from
        
        Raises:
            NoneInjectorException: If there's no routes in module to load
        """
        try:
            module = load_module(module, self.injector)
        except RuntimeError:
            pass

        children = module._injector.get("ROUTER_MODULE")
        self.__process_children(children, module._injector)
    
    def load_routes(self):
        """
        Loads all routes of controller into `APIRouter` or `RouterNode`
        """
        routes = self.controller.__controller__.get_routes()
        for callback, metadata in routes.items():
            if not self.router.prefix and not metadata.get("path", None):
                metadata["path"] = "/"
            self.router.add_api_route(endpoint=callback, **metadata)
            
            self.logger.debug(f"Route {metadata['path']} of {self.controller.__class__.__name__} successfully mounted to webserver")

    def hydrate(self):
        if self.route.get("load_children", None):
            self.__load_children(self.route["load_children"]())

        if is_direct_controller(self.route) and not is_module_controller(self.route):
            self.__create_controller(self.route["controller"], None) # type: ignore
            return

        if is_module_controller(self.route):
            module = self.route["load_controller"]()
            try:
                module = load_module(module) # type: ignore
            except RuntimeError:
                pass
            
            if is_direct_controller(self.route):
                module, controller = unwrap_module_controller(module, self.route["controller"])
            
            else:
                module, controller = unwrap_module_controller(module)
            
            self.__create_controller(controller, module)
            return
        
        raise RuntimeError("Failed to load module or controller, please check your route graphs `controller` or `load_controller` parameters are specified correctly!")
    
    def __create_controller(
        self, 
        controller: type[ControllerRef],
        parent: type[AscModuleRef] | type[ControllerRef] | None = None
    ):
        if not parent and not controller.__controller__.standalone:
            raise NotStandaloneError(f"Controller {controller} must be standalone controller to be loaded directly in router!")
        
        self.logger.debug(f"Loading & Hydrating controller {controller.__name__}")

        if parent:
            self.logger.debug(f"Mounting non-standalone controller [cyan]{controller.__name__}[/cyan] to router-path [yellow]{self.route['path']}[/yellow]")
            self.controller = parent.__asc_module__.activate_consumer(controller)
            self.logger.info(f"Controller [cyan]{controller.__name__}[/cyan] successfully loaded")
            return
        
        # Create and hydrate controller
        try:
            self.logger.debug(f"Mounting controller [cyan]{controller.__name__}[/cyan] to router-path [yellow]{self.route['path']}[/yellow]")
            self.controller = load_module(controller, self.injector)
            self.controller = self.controller.__controller__.hydrate_controller(self.injector)
            self.logger.info(f"Controller [cyan]{controller.__name__}[/cyan] successfully loaded")
        except RuntimeError:
            self.controller = controller