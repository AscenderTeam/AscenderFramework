from asyncio import iscoroutine
from enum import Enum
import inspect
from typing import TYPE_CHECKING, Any, Sequence, TypeVar

from fastapi import APIRouter
from fastapi.datastructures import Default
from fastapi.params import Depends

from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule
from ascender.core.di.hierarchy_module import HierarchyModule
from ascender.core.di.provider import Provider
from ascender.core.registries.service import ServiceRegistry
from ascender.core.application import Application


T = TypeVar("T")


class Controller(HierarchyModule):

    def __init__(
        self,
        standalone: bool = True,
        name: str | None = None,
        tags: list[str] = [],
        prefix: str = "",
        suffix: str = "",
        guards: Sequence[Depends] = [],
        *,
        imports: list[type[T | AbstractModule]] = [],
        providers: list[T | AbstractModule] = [],
        exports: list[T | AbstractModule] = [],
    ) -> None:
        self.name = name
        self.tags = tags
        self.prefix = prefix
        self.suffix = suffix
        self.guards = guards
        self.standalone = standalone

        if (len(imports) or len(providers)) and not self.standalone:
            raise ValueError(
                "Non-standalone controller cannot contain imports or providers!")

        self.imports = imports
        self.providers = providers
        self.exports = exports

    # region lifecycle
    def on_application_bootstrap(self):
        async def bootstrap_wrapper(cls, application: Application):
            self.inject_lazy_dependencies()
            for o in self._factory_scope:
                if isinstance(o, AbstractModule):
                    if inspect.iscoroutinefunction(o.on_application_bootstrap):
                        await o.on_application_bootstrap(application)
                        continue

                    o.on_application_bootstrap(application)
                    self.handle_factories()
                    self.inject_lazy_dependencies()

                self.handle_factories()
                self.inject_lazy_dependencies()

            for t, o in self._module_scope.items():
                if issubclass(t, AbstractModule):
                    if inspect.iscoroutinefunction(o.on_application_bootstrap):
                        await o.on_application_bootstrap(application)
                        continue

                    o.on_application_bootstrap(application)

        return bootstrap_wrapper

    def on_application_shutdown(self):
        async def shutdown_wrapper(cls, application: Application):
            for t, o in self._module_scope.items():
                if issubclass(t, AbstractModule):
                    if inspect.iscoroutinefunction(o.on_application_shutdown):
                        await o.on_application_shutdown(application)
                        continue

                    o.on_application_shutdown(application)

        return shutdown_wrapper

    def handle_providers(self):
        self.providers = self.sort_dependencies(list(map(lambda p: p.injectable if isinstance(p, Provider) and
                                                         not p.factory_method else p, self.providers)))
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

    def handle_exports(self):
        for export in self.exports:
            self.handle_export(export)

    def __call__(self, cls: object):
        router = APIRouter(tags=self.tags, prefix=self.suffix)

        def handle_injections():

            self.handle_providers()
            self.handle_imports()

            self.handle_exports()
            cls._controller_scope = self._module_scope
    
            controller = self.inject_eager_dependency(cls)
            self._lazy_loading_dependencies.append(controller)

            return controller

        cls.bootstrap = handle_injections
        cls._router_prefix = self.prefix
        cls._router_name = self.name
        cls.on_application_bootstrap = self.on_application_bootstrap()
        cls.on_application_shutdown = self.on_application_shutdown()

        def load_routes(cls, router: APIRouter):
            for name, method in cls.__class__.__dict__.items():
                # Complex FastAPI wrapper
                if hasattr(getattr(cls, name), "_controller_keyword_args") and hasattr(getattr(cls, name), "_controller_method"):
                    router.add_api_route(endpoint=getattr(cls, name), methods=[
                        method._controller_method], **method._controller_keyword_args)

        cls.load_routes = load_routes
        cls.router = router
        cls.standalone = self.standalone
        cls.__declaration_type__ = "controller"

        return cls


def Get(path: str = "/", response_model: Any = Default(None),
        status_code: int | None = None,
        tags: list[str | Enum] = None, **kwargs):

    if not path.startswith("/"):
        path = f"/{path}"

    def decorator(func):
        func._controller_keyword_args = {
            "path": path,
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags,
            "dependencies": getattr(func, "_dependencies", []),
            **kwargs,
        }
        func._controller_method = "GET"
        return func

    return decorator


def Post(path: str = "/", response_model: Any = Default(None),
         status_code: int | None = None,
         tags: list[str | Enum] = None, **kwargs):

    if not path.startswith("/"):
        path = f"/{path}"

    def decorator(func):
        func._controller_keyword_args = {
            "path": path,
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags,
            "dependencies": getattr(func, "_dependencies", []),
            **kwargs,
        }
        func._controller_method = "POST"
        return func

    return decorator


def Put(path: str = "/", response_model: Any = Default(None),
        status_code: int | None = None,
        tags: list[str | Enum] = None, **kwargs):

    if not path.startswith("/"):
        path = f"/{path}"

    def decorator(func):
        func._controller_keyword_args = {
            "path": path,
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags,
            "dependencies": getattr(func, "_dependencies", []),
            **kwargs,
        }
        func._controller_method = "PUT"
        return func

    return decorator


def Patch(path: str = "/", response_model: Any = Default(None),
          status_code: int | None = None,
          tags: list[str | Enum] = None, **kwargs):

    if not path.startswith("/"):
        path = f"/{path}"

    def decorator(func):
        func._controller_keyword_args = {
            "path": path,
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags,
            "dependencies": getattr(func, "_dependencies", []),
            **kwargs,
        }
        func._controller_method = "PATCH"
        return func

    return decorator


def Delete(path: str = "/", response_model: Any = Default(None),
           status_code: int | None = None,
           tags: list[str | Enum] = None, **kwargs):

    if not path.startswith("/"):
        path = f"/{path}"

    def decorator(func):
        func._controller_keyword_args = {
            "path": path,
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags,
            "dependencies": getattr(func, "_dependencies", []),
            **kwargs,
        }
        func._controller_method = "DELETE"
        return func

    return decorator
