from typing import Any, Callable, MutableMapping, Sequence, TypeVar, cast

from ascender.core.di.injector import AscenderInjector
from ascender.core.struct.module import AscModule
from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef

from ascender.core.di.interface.provider import Provider
from ascender.guards.guard import Guard
from ascender.guards.paramguard import ParamGuard


T = TypeVar("T")


class Controller(AscModule):
    controller_ref: type[ControllerRef] | ControllerRef

    def __init__(
        self,
        standalone: bool = True,
        name: str | None = None,
        tags: list[str] = [],
        prefix: str = "",
        suffix: str = "",
        guards: Sequence[type[Guard] | type[ParamGuard]] = [],
        *,
        imports: Sequence[type[AscModuleRef | ControllerRef]] = [],
        providers: Sequence[Provider] = [],
        exports: Sequence[type[T] | str] = [],
    ) -> None:
        self.name = name
        self.tags = tags
        self.prefix = prefix
        self.suffix = suffix
        self.guards = guards
        self.standalone = standalone

        self.imports = imports
        self.providers = providers
        self.exports = exports

    def get_routes(self):
        """
        Gets routes defined in controller, it returns them in specific controller-metadata format.
        controller-metadata (cmetadata) is a Mapping containing parameters for FastAPI API Router.

        Raises:
            ValueError: If `get_routes` is being called when controller is not created and hydrated.

        Returns:
            cmetadata: Controller's metadata
        """
        if isinstance(self.controller_ref, type):
            raise ValueError(f"Controller {self.controller_ref.__name__} was not hydrated. "
                             "Ensure the controller is properly instantiated and hydrated before calling `get_routes`.")

        routes: MutableMapping[Callable[..., Any], Any] = {}

        for name, method in self.controller_ref.__class__.__dict__.items():
            if hasattr(method, "__cmetadata__"):
                # Monkey-patched metadata from controller's methods which were wrapped by @Get, @Post, @Put, @Patch, @Delete decorators
                routes[getattr(self.controller_ref, name)
                       ] = method.__cmetadata__

        return routes

    def hydrate_controller(self, _injector: AscenderInjector):
        """
        Hydrates the application with controller, returns controller reference as initiated object

        Args:
            _parent (type[AscModuleRef] | ControllerRef | type[ControllerRef] | None, optional): Parent module/injector of the controller. Defaults to None.

        Returns:
            ControllerRef: Controller Reference Object
        """
        if not isinstance(self.controller_ref, type):
            raise RuntimeError(f"Controller {self.controller_ref.__class__.__name__} is already loaded and hydrated")
        
        # Get injector from controller's DI module
        self.controller_ref = _injector.inject_factory_def(self.controller_ref)()
        
        return self.controller_ref

    def create_module(self, _parent):
        """
        Instantiates controller as an module same as AscModule

        Args:
            _parent: Parent injector of the module. If there is no parent, pass `RootInjector.existing_injector` to this parameter
        """
        return super().create_module(_parent)

    def __call__(self, controller_ref) -> Any:
        self.controller_ref = controller_ref
        self.controller_ref.__controller__ = self

        # Set `__asc_module__` metadata if standalone
        if self.standalone:
            super().__init__(self.imports, [self.controller_ref, *self.guards], self.providers, self.exports)
            super().__call__(controller_ref)

        return self.controller_ref
