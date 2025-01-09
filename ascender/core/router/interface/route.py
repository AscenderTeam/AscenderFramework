from typing import Callable, NotRequired, Sequence, TypedDict

from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef
from ascender.guards.guard import Guard
from ascender.guards.paramguard import ParamGuard


class RouterRoute(TypedDict):
    
    path: str
    """
    Path of route, paths are specified in next format: `{path_name}`. Will be applied to all routes of controller.
    Also it will be used as base path for children of this route
    """
    tags: NotRequired[Sequence[str]]
    """
    Tags that separates this controller from others. Also it will be applied to the children of the route
    """
    include_in_schema: NotRequired[bool]
    """
    To include (or not) all the *path operations* in this router in the
    generated OpenAPI.

    This affects the generated OpenAPI (e.g. visible at `/docs`).
    """
    deprecated: NotRequired[bool]
    """
    Mark all *path operations* in this router as deprecated.
    It will be added to the generated OpenAPI (e.g. visible at `/docs`).
    """
    controller: NotRequired[type[ControllerRef]]
    """
    Controller which will be bound to this route.
    
    NOTE: In this scenario, use only controllers which are marked as `standalone` and have `standalone=True` mark
    """
    load_controller: NotRequired[Callable[[], type[AscModuleRef]]]
    """
    Module which will be loaded and one of controllers in it's consumer `declarations` will be used and bound to this route.

    NOTE: Use this if you have non-standalone and module-based controller
    """

    single_guards: Sequence[Guard]
    """
    Applies Ascender Framework's single guards to all routes of controller

    NOTE: The guard specified won't inherit and be able to inject dependencies of loaded controller or module. 
    It will only have access to root or global scope
    """

    param_guards: Sequence[ParamGuard]
    """
    Applies Ascender Framework's parametrized guards to all routes of controller.

    NOTE: All routes of controller will have some parameters defined in guards specified here. Make sure to define them in all methods of routes!
    
    NOTE: The guard specified won't inherit and be able to inject dependencies of loaded controller or module. 
    It will only have access to root or global scope
    """

    # region children
    children: NotRequired[Sequence["RouterRoute"]]
    """
    Nested level of routes that are children of this route. They will inherit current route's configurations
    """

    load_children: NotRequired[Callable[[], AscModuleRef]]
    """
    Loads all route's from ModuleRouter defined in AscModule and assignes them as current route's children
    """
