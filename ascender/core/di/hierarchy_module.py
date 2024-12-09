from typing import Any, Callable, TypeVar

from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule
from ascender.core.di.di_module import DIModule
from ascender.core.registries.service import ServiceRegistry

import inspect

from ascender.guards.guard import Guard
from ascender.guards.paramguard import ParamGuard


T = TypeVar("T")


class HierarchyModule(DIModule):
    
    _lazy_loading_dependencies: list[T | AbstractModule] = []
    _factory_scope: list[AbstractFactory] = []

    def handle_import(self, module: type[T]):
        module = module()
        
        if not hasattr(module, "bootstrap"):
            raise TypeError(f"Module {module.__name__} is not an AscModule")
        
        module.bootstrap() # Loads the module as per needed

        if not (_submodule_scope := getattr(module, "_module_scope", None)):
            raise TypeError(
                f"Module {module.__name__} is corrupted and cannot be imported")

        self._module_scope = {**self._module_scope, **_submodule_scope}

    def handle_export(self, export_dependency: type[T]):
        """
        Exports local object to the global service registry.
        """
        service_registry = ServiceRegistry()
        global_di_object = service_registry.get_singletone(export_dependency)
        local_di_object = self._module_scope.get(export_dependency, None)

        if not local_di_object:
            raise TypeError(
                "Can't export non-local dependency. Please make sure you've defined {object}".format(object=export_dependency.__name__))

        if global_di_object:
            return None

        service_registry.add_singletone(export_dependency, local_di_object)

    def handle_provider(
        self, 
        provider: type[T | AbstractModule] | AbstractFactory | AbstractModule, 
        factory_method: Callable[..., type[T]] | Any | None = None, 
        is_lazy: bool = True
    ):
        """
        Handles the initialization of provider objects in the local module scope.
        """
        # Resolve the appropriate provider type
        provider_type = type(provider) if provider.__class__ != type else provider

        # Check global and local dependencies
        service_registry = ServiceRegistry()
        global_di_object = service_registry.get_singletone(provider_type)
        local_di_object = self._module_scope.get(provider_type)

        # If the provider is already registered globally or locally, no action needed
        if global_di_object or local_di_object:
            return

        if isinstance(provider, AbstractFactory):
            # Handle AbstractFactory
            self._lazy_loading_dependencies.append(provider)
            self._factory_scope.append(provider)
            return

        if factory_method:
            if not inspect.ismethod(factory_method):
                raise TypeError("Provided factory method is not a valid method!")

            if provider.__class__ != type:
                raise TypeError("Cannot resolve provider type for the factory provider!")

            if is_lazy:
                self._lazy_loading_dependencies.append(factory_method())
            else:
                self._module_scope[provider] = factory_method()
            return

        # Handle AbstractModule or type-based providers
        if provider.__class__ == type:
            instance = self.inject_eager_dependency(provider)
            self._module_scope[provider] = instance

            if is_lazy:
                self._lazy_loading_dependencies.append(instance)

            # Call on_module_init if the provider is an AbstractModule
            if issubclass(provider, AbstractModule):
                instance.on_module_init()
        else:
            # Handle non-module providers
            self._module_scope[provider_type] = provider
            if is_lazy:
                self._lazy_loading_dependencies.append(provider)

    def handle_declaration(
            self,
            declaration: type[T | AbstractModule | Guard]
    ):
        """
        Handles in-module declarations like (Controllers, Guards and etc) creating a dependency and storing it
        """
        service_registry = ServiceRegistry()
        global_di_object = service_registry.get_singletone(declaration)
        local_di_object = self._module_scope.get(declaration, None)

        if not global_di_object and not local_di_object:
            if issubclass(declaration, (Guard, ParamGuard)):
                declaration.__di_module__ = self
                return
            declaration_dependency = self.inject_eager_dependency(declaration)
            self._module_scope[declaration] = declaration_dependency
            
            # Add in case if there are lazy loaders
            self._lazy_loading_dependencies.append(self._module_scope[declaration])
    
    def handle_factories(self):
        for factory_object in self._factory_scope:
            factory_injectables = factory_object.__factory__()

            for t, o in factory_injectables.items():
                if t in self._module_scope:
                    continue
                
                self._module_scope[t] = o
                self._lazy_loading_dependencies.append(o)

            # if factory_object in self._lazy_loading_dependencies:
            #     self._lazy_loading_dependencies.remove(factory_object)
    
    def inject_eager_dependency(self, dependency: type[T | AbstractModule]):
        inject_params = self.inject(dependency.__init__)

        return dependency(**inject_params)

    def inject_lazy_dependencies(self):
        for dependency in self._lazy_loading_dependencies:
            inject_params = self.inject(dependency)

            for param_name, param_obj in inject_params.items():
                setattr(dependency, param_name, param_obj)