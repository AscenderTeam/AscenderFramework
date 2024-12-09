import inspect
from typing import TYPE_CHECKING, Any
from typing import TypeVar
from inflection import underscore

from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule
from ascender.core.di.hierarchy_module import HierarchyModule
from ascender.core.di.provider import Provider
from ascender.core.registries.service import ServiceRegistry

if TYPE_CHECKING:
    from ascender.core.application import Application


T = TypeVar("T")


class AscModule(HierarchyModule):
    module_name = ""

    def __init__(
        self,
        imports: list[type[T]],
        declarations: list[type[T]],
        providers: list[AbstractModule | AbstractFactory | T | Provider],
        exports: list[type[T | AbstractModule]]
    ):
        """
        A dependency injection module system for managing service imports, providers, and exports.

        Attributes:
            module_name (str): The name of the module in snake_case.
            _module_scope (dict): Local scope for storing instantiated objects.
        """
        self.imports = imports
        self.providers = providers
        self.declarations = declarations
        self.exports = exports

    def handle_providers(self):
        self.providers = self.sort_dependencies(list(map(lambda p: p.injectable if isinstance(p, Provider) and
                                                         not p.factory_method else p, self.providers)))
        # print(self.providers)
        for provider in self.providers:
            if isinstance(provider, Provider):
                if not provider.injectable:
                    raise ValueError(
                        "Provider Injectable should be an injectable class, got Nontype object")

                if provider.provider_type == "abstract_factory":
                    self.handle_provider(
                        provider.injectable, factory_method=None, is_lazy=provider.is_lazy)

                if provider.provider_type == "classic":
                    self.handle_provider(
                        provider.injectable, factory_method=None, is_lazy=provider.is_lazy)

                if provider.provider_type == "factory_method":
                    self.handle_provider(
                        provider.injectable, factory_method=provider.factory_method, is_lazy=provider.is_lazy)
                continue

            if inspect.ismethod(provider) or inspect.isfunction(provider):
                if not provider.__annotations__.get("return"):
                    raise TypeError(
                        "Failed to recognize any injectable from provided function/method!")
                if not getattr(provider.__annotations__["return"], "__class__"):
                    raise TypeError(
                        "Failed to recognize any injectable from provided function/method!")
                if provider.__annotations__["return"].__class__ != type:
                    raise TypeError(
                        "Failed to recognize any injectable from provided function/method!")

                self.handle_provider(provider.__annotations__[
                                     "return"], factory_method=provider)
                continue

            self.handle_provider(provider)

    def handle_imports(self):
        for imported_module in self.imports:
            if not hasattr(imported_module, "asc_module") and not hasattr(imported_module, "bootstrap"):
                raise TypeError(
                    f"{imported_module.__name__} is not importable AscModule!")

            self.handle_import(imported_module)

    def handle_declarations(self):
        for declaration in self.declarations:
            if not hasattr(declaration, "__declaration_type__"):
                raise TypeError(
                    "Only controllers and guards are allowed to be used in declarations of AscModule!")

            self.handle_declaration(declaration)

    def handle_exports(self):
        for export in self.exports:
            self.handle_export(export)

    # region Lifecycle hooks
    async def on_application_bootstrap(self, application: "Application"):
        # async def bootstrap_wrapper(cls, application: "Application"):

        # Primary injection for providers
        self.inject_lazy_dependencies()

        for o in self._factory_scope:
            if isinstance(o, AbstractModule):
                if inspect.iscoroutinefunction(o.on_application_bootstrap):
                    await o.on_application_bootstrap(application)
                    continue

                o.on_application_bootstrap(application)
                self.handle_factories()
                self.inject_lazy_dependencies()

        for t, o in self._module_scope.items():
            if issubclass(t, AbstractModule):
                if inspect.iscoroutinefunction(o.on_application_bootstrap):
                    await o.on_application_bootstrap(application)
                    continue

                o.on_application_bootstrap(application)

    async def on_application_shutdown(self, application: "Application"):
        async def shutdown_wrapper(cls, application: "Application"):
            for t, o in self._module_scope.items():
                if issubclass(t, AbstractModule):
                    if inspect.iscoroutinefunction(o.on_application_shutdown):
                        await o.on_application_shutdown(application)
                        continue

                    o.on_application_shutdown(application)

        return shutdown_wrapper

    def __call__(self, cls: Any):
        """
        Makes the AscModule class function as a decorator.

        When the AscModule is applied to a class, it processes the following:
        - Imports: Resolves dependencies for imported services.
        - Providers: Initializes and injects dependencies into provided services.
        - Exports: Registers local services in the global service registry.

        Args:
            cls (Any): The class being decorated.

        Example Usage:
            @AscModule(
                imports=[DependencyA, DependencyB],
                providers=[ProviderA(), ProviderB()],
                exports=[ExportedService]
            )
            class MyModule:
                pass
        """
        self.module_name = underscore(cls.__name__)

        def bootstrap(cls):
            service_registry = ServiceRegistry()
            self.handle_providers()
            self.handle_imports()
            self.handle_declarations()

            self.handle_exports()

            cls._module_scope = self._module_scope

            service_registry.add_singletone(type(cls), cls)

        cls.bootstrap = bootstrap
        cls.on_application_bootstrap = self.on_application_bootstrap
        cls.on_application_shutdown = self.on_application_shutdown
        cls.asc_module = self.module_name
        return cls
