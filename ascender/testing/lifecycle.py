from typing import Sequence

import pytest

# from app_module import AppModule
from ascender.common.api_docs import DefineAPIDocs
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.applications.application import Application
from ascender.core.applications.root_injector import RootInjector
from ascender.core.database.engine import DatabaseEngine
from ascender.core.di.abc.base_injector import Injector
from ascender.core.di.interface.provider import Provider
from ascender.core.router.graph import RouterGraph
from ascender.core.router.provide import provideRouter
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.module import load_module


class AscenderTestLifecycle:
    def __init__(
        self, 
        app_module: type[AscModuleRef] | None = None, 
        providers: list[Provider] | None = None
    ) -> None:
        """
        Ascender Testing Lifecycle Manager, it's mandatory to define it in conftests.
        Manages lifecycles from beginning of the tests and to end, initializes ascender framework's features and DI.

        Args:
            app_module (AppModule | None, optional): The application module to use. Defaults to None.
            providers (list[Provider] | None, optional): The list of providers to use. Defaults to None.

        Raises:
            ValueError: If neither app_module nor providers is provided.
        """
        if app_module is None and providers is None:
            raise ValueError("Either app_module or providers must be provided.")
        
        self.app_module = app_module
        self.providers = providers
        self.configs = _AscenderConfig()
        self.application = None

    def begin_session(self, session: pytest.Session):
        """
        Hook for beginning the entire application session.
        """
        _AscenderConfig.is_test = True
        self.configs.is_test = True
        
        application_provider = [
        provideRouter([]),
        {
            "provide": Application,
            "use_factory": lambda injector: Application(
                injector.get(RouterGraph),
                cli_settings=injector.get("ASC_CLI_COMMAND", not_found_value=[]),
                docs_settings=DefineAPIDocs(),
                database_settings=injector.get(DatabaseEngine, not_found_value=None, options={
                    "optional": True
                }),
                middleware_settings=injector.get("ASC_MIDDLEWARE", not_found_value=[])
            ),
            "deps": [Injector]
        }]

        root_injector = RootInjector().create([(self.providers or []), application_provider])

        if self.app_module:
            module = load_module(self.app_module, root_injector.existing_injector)
            
            assert module._injector
            self.application = module._injector.get(Application)
            return
        self.application = root_injector.existing_injector.get(Application)

    def before_test(self):
        """
        Pytest Interop.
        Hook to run before test.
        """
        pass

    def after_test(self):
        """
        Pytest Interop.
        Hook to run after test.
        """
        pass
    
    def end_session(self):
        """
        Hook for ending the entire application session.
        """
        self.application = None