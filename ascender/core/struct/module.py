from typing import Any, MutableSequence, Sequence, TypeVar

from ascender.core.di.create import create_injector
from ascender.core.di.injector import AscenderInjector
from ascender.core.di.interface.provider import Provider
from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.hydrate_consumer import foreach_consumers
from ascender.core.utils.module import load_module, module_import
from ascender.guards.guard import Guard
from ascender.guards.paramguard import ParamGuard


T = TypeVar("T")


class AscModule:
    module_instance: type[AscModuleRef]
    imported_modules: MutableSequence[type[AscModuleRef]]

    consumers: MutableSequence[type[ControllerRef] | type[Guard] | type[ParamGuard]]
    active_consumers: MutableSequence[ControllerRef] = []

    def __init__(
        self,
        imports: Sequence[type[AscModuleRef | ControllerRef]],
        declarations: Sequence[type[T]],
        providers: MutableSequence[Provider],
        exports: Sequence[type[T] | str]
    ) -> None:
        """
        Ascender Module is hierarchy module for handling dependency injection seamlessly.

        Args:
            imports (list[type[T]]): Modules to import, providers specified in their `exports` will be injected into this module
            declarations (list[type[T]]): Declarations, that will be defined in this module.
            providers (list[Provider]): Providers that will supply this module
            exports (list[type[T]]): Exports that will out of encapsulation and will be imported in other module, if this module will be imported to `AscModule` module
        """
        self.imports = imports
        self.declarations = declarations
        self.providers = providers
        self.exports = exports

        self.imported_modules = []
        self.consumers = []
    
    def create_module(self, _parent: type[AscModuleRef] | ControllerRef | type[ControllerRef] | AscenderInjector):
        """
        Instantiates module with assigned parent and loads providers.

        Args:
            _parent (type[AscModuleRef]): Parent module, by default it should be root
        """
        _parent_injector = _parent._injector if not isinstance(_parent, AscenderInjector) else _parent
        # Creates `AscenderInjector` instance on current module. Also assigns parent if there is
        self.module_instance._injector = create_injector(
            self.providers,
            parent=_parent_injector if isinstance(_parent_injector, AscenderInjector) else None
        )
        
        # Processes current module after injector being created.

        # Handle middle hydration of declarations
        foreach_consumers(self.module_instance, self.declarations, lambda c: self.consumers.append(c))
        
        # Handle imports
        self.__process_imports()
        
        return self.module_instance

    def __process_imports(self):
        for _imported in self.imports:
            if not hasattr(_imported, "__asc_module__"):
                raise RuntimeError(f"Failed to resolve AscModule {_imported.__name__}!")
            try:
                loaded_module = load_module(_imported)
            except RuntimeError:
                loaded_module = _imported

            module_import(loaded_module, self.module_instance._injector)
            self.imported_modules.append(loaded_module)
    
    def __call__(self, module_instance) -> Any:
        self.module_instance = module_instance
        self.module_instance.__asc_module__ = self # type: ignore

        return self.module_instance
    
    def activate_consumer(self, consumer: type[ControllerRef]) -> ControllerRef:
        if not hasattr(consumer, "__controller__"):
            raise RuntimeError("Currently, only controller can be active consumer!")
        
        if consumer not in self.consumers:
            raise RuntimeError(f"Declaration {consumer.__name__} for module {self.module_instance.__name__} not found!")
        return consumer.__controller__.hydrate_controller(self.module_instance._injector)
