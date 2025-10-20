from collections.abc import MutableSequence
from typing import Any, Mapping, TypeVar

from sqlalchemy import Sequence

from ascender.core.applications.root_injector import RootInjector
from ascender.core.di.interface.provider import Provider
from ascender.core.di.test_injector import TestInjector
from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module import AscModule
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.module import load_module
from ascender.testing.mock_dependency import MockDependency


T = TypeVar("T")


class TestClient:
    """
    HTTP test client for loading controllers, dependencies, guards and many other declarations and providers. Universal mock testing client.
    """
    
    def __new__(cls, _framework_dep: type[T], mocks: Mapping[str | type, object | MockDependency | type]) -> T:
        """
        Create a new instance of the test client.

        A new instance with injected mocks for the specified dependencies on the framework dependency injection requirements.
        
        ```python
        from ascender.testing import TestClient, MockDependency
        
        my_controller = TestClient(
            MyController,
            mocks={
                MyService: MockDependency(
                    get_data=lambda self: "mocked data"
                )
            }
        )
        ```
        
        Args:
            _framework_dep (type[T]): The framework dependency to instantiate.
            mocks (Mapping[str | type, object | MockDependency | type]): A mapping of dependencies to their mock implementations.
        
        Returns:
            T: An instance of the framework dependency with mocks applied.
        """
        injector = cls._get_mocks_injector(mocks)
        # create _framework_dep with mocks applied
        instance = injector.inject_factory_def(_framework_dep)
        
        return instance()
    
    @staticmethod
    def _get_mocks_injector(mocks: Mapping[str | type, object | MockDependency]):
        providers: list[Provider] = []
        
        for key, mock in mocks.items():
            if isinstance(mock, MockDependency):
                providers.append({
                    "provide": key,
                    "use_class": mock._as_object(f"Mocked{key.__name__ if isinstance(key, type) else key}"),
                })
            else:
                if not isinstance(mock, type):
                    providers.append({
                        "provide": key,
                        "use_value": mock
                    })
                
                else:
                    providers.append({
                        "provide": key,
                        "use_class": mock
                    })
        
        return TestInjector(providers=providers, parent=RootInjector.injector) # type: ignore # noqa: F821 # RootInjector is automatically TestInjector if in testing mode
    
    @staticmethod
    def create_testing_module(
        imports: Sequence[type[AscModuleRef | ControllerRef]],
        declarations: Sequence[type[Any]],
        providers: MutableSequence[Provider],
        exports: Sequence[type[Any] | str],
        name: str | None = None,
    ) -> type[AscModuleRef]:
        """
        Create a testing `AscModule` with the given imports, declarations, providers, and exports.
        
        Args:
            imports (Sequence[type[AscModuleRef | ControllerRef]]): The modules or controllers to import.
            declarations (Sequence[type[Any]]): The declarations for the module.
            providers (MutableSequence[Provider]): The providers for the module.
            exports (Sequence[type[Any] | str]): The exports for the module.
            name (str | None, optional): The name of the testing module (used as object name). Defaults to None.
        
        Returns:
            type[AscModuleRef]: The created testing module reference.
        """
        # Create a testing module with the given imports, declarations, providers, and exports
        module = AscModule(
            imports=imports, # type: ignore
            declarations=declarations, # type: ignore
            providers=providers,
            exports=exports # type: ignore
        )(type(name or "TestingModule"))
        module_ref = load_module(module)
        
        assert module_ref._injector is not None
        return module_ref