from inflection import titleize
from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule
from ascender.clis.cli_module import CliModule
from ascender.common.api_docs import DefineAPIDocs
from ascender.core.cli.provider import CLIProvider
from typing import Any, Callable
from fastapi import FastAPI

import inspect
from ascender.core.cli.processor import CLI
from ascender.core.di.hierarchy_module import HierarchyModule
from ascender.core.di.provider import Provider
from ascender.core.registries.service import ServiceRegistry

from ascender.core.types import Controller, IBootstrap
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case


class Application:

    _lazy_loading_dependencies: list[Any | AbstractFactory | AbstractModule] = []
    _factory_scope: list[AbstractFactory] = []

    def __init__(
        self,
        main_controller: Controller,
        bootstrap: IBootstrap
    ) -> None:
        self.app = FastAPI(title="Ascender Framework API", docs_url=None, redoc_url=None)

        self.main_controller = main_controller
        self.bootstrap = bootstrap

        self.service_registry = ServiceRegistry()

        # self.loader_module = Loader(self.app, self, controllers, self._plugin_loader)
        self.security = None

        # Initialize CLI module
        self.__cli = CLI(self, app_name="AscCLI")

        # Inject application itself into DI
        self.service_registry.add_singletone(Application, self)

    async def load_controller(self, controller: Controller, _use_name_prefix: bool = True):
        # Check if controller is standalone
        if not controller.standalone:
            raise TypeError("Main Controller should be standalone!")
        
        controller = controller.bootstrap()
        
        controller.load_routes(controller.router)
        await controller.on_application_bootstrap(application=self)
        
        _url_prefix = ""
        
        if _use_name_prefix:
            if controller._router_name:
                _url_prefix = controller._router_name
            else:
                _url_prefix = kebab_case(controller.__class__.__name__.removesuffix("Controller"))


        self.app.include_router(
            controller.router, 
            tags=[titleize(pascal_case(_url_prefix))]
        )
        self.main_controller = controller

    def define_api_docs(self, configs: DefineAPIDocs):
        self.app = configs.update_instance(self.app)

    def run_cli(self) -> None:
        # NOTE: For custom CLIs that were used in provider
        if cli_provider := self.service_registry.resolve(CLIProvider):
            cli_provider.invoke(self.__cli)

        inner_provider = CLIProvider.fromModule(CliModule())
        inner_provider.invoke(self.__cli)

        self.__cli.run()

    def get_version(self) -> str:
        return "v1.3.0-beta.5"

    def load_providers(self):
        hierarchy_module = HierarchyModule()
        providers = self.bootstrap["providers"]

        providers = hierarchy_module.sort_dependencies(list(map(lambda p: p.injectable if isinstance(p, Provider) and
                                                    not p.factory_method else p, providers)))

        for provider in providers:
            if isinstance(provider, DefineAPIDocs):
                self.define_api_docs(provider)
                continue

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
        
        self.app.add_event_handler("startup", self._startup_handler)
        self.app.add_event_handler("shutdown", self._shutdown_handler)

    def handle_provider(
        self, 
        provider: type[Any | AbstractModule] | AbstractFactory | AbstractModule, 
        factory_method: Callable[..., type[Any]] | Any | None = None, 
        is_lazy: bool = True
    ):
        """
        Handles the initialization of provider objects in the local module scope.
        """
        # Resolve the appropriate provider type
        provider_type = type(provider) if provider.__class__ != type else provider

        # Check global and local dependencies
        global_di_object = self.service_registry.get_singletone(provider_type)

        # If the provider is already registered globally or locally, no action needed
        if global_di_object:
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
                self.service_registry.add_singletone(provider, factory_method())
            return

        # Handle AbstractModule or type-based providers
        if provider.__class__ == type:
            instance = self.inject_eager_dependency(provider)
            self.service_registry.add_singletone(provider, instance)

            if is_lazy:
                self._lazy_loading_dependencies.append(instance)

            # Call on_module_init if the provider is an AbstractModule
            if issubclass(provider, AbstractModule):
                instance.on_module_init()
        else:
            if isinstance(provider, AbstractModule):
                provider.on_module_init()
            # Handle non-module providers
            self.service_registry.add_singletone(type(provider), provider)
            if is_lazy:
                self._lazy_loading_dependencies.append(provider)

    def inject_eager_dependency(self, dependency: Any):
        params = self.service_registry.get_parameters(dependency.__init__)

        return dependency(**params)

    def inject_lazy_dependencies(self):
        for dependency in self._lazy_loading_dependencies:
            params = self.service_registry.get_parameters(dependency)

            for k, o in params.items():
                setattr(dependency, k, o)
    
    def handle_factories(self):
        for factory_object in self._factory_scope:
            factory_injectables = factory_object.__factory__()

            for t, o in factory_injectables.items():
                if t in self.service_registry.singletones:
                    continue
                
                self.service_registry.add_singletone(t, o)
                self._lazy_loading_dependencies.append(o)

    def __call__(self) -> Any:
        self.load_providers()

        return self.app

    def launch(self):
        self.load_providers()
        # After providing providers, run CLIs together
        self.run_cli()

    async def _startup_handler(self):
        main_providers = self.service_registry.singletones.copy()
        
        self.inject_lazy_dependencies()

        for o in self._factory_scope:
            if isinstance(o, AbstractModule):
                if inspect.iscoroutinefunction(o.on_application_bootstrap):
                    await o.on_application_bootstrap(self)
                    continue

                o.on_application_bootstrap(self)
            self.handle_factories()
            self.inject_lazy_dependencies()

        await self.load_controller(self.main_controller, True)

        for t, o in main_providers.items():
            if hasattr(o, "on_application_bootstrap"):
                if not inspect.ismethod(o.on_application_bootstrap):
                    continue

                if inspect.iscoroutinefunction(o.on_application_bootstrap):
                    await o.on_application_bootstrap(self)
                    continue

                o.on_application_bootstrap(self)

        self.inject_lazy_dependencies()

    async def _shutdown_handler(self):
        await self.main_controller.on_application_shutdown(self)
        
        for t, o in self.service_registry.singletones.items():
            if hasattr(o, "on_application_shutdown"):
                if not inspect.ismethod(o.on_application_shutdown):
                    continue

                if inspect.iscoroutinefunction(o.on_application_shutdown):
                    await o.on_application_shutdown(self)
                    continue

                o.on_application_shutdown(self)
