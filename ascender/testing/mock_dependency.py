
from typing import TypeVar


T = TypeVar("T")

class MockDependency:
    def __init__(self, **values) -> None:
        """
        A lightweight mock utility for simulating dependencies in Ascender Framework tests.

        `MockDependency` lets you create simple mock objects with dynamic attributes or methods, 
        without requiring external mocking libraries.

        These mocks can be used in Ascender's dependency injection system (via `TestClient` or `TestInjector`),
        or as standalone mock objects.

        Example:
        ```python
        mock_dep = MockDependency(
            method=lambda self: "mocked method",
            value=42
        )
        mock_obj = mock_dep._as_object("MyMock")

        print(mock_obj.method())  # -> "mocked method"
        print(mock_obj.value)     # -> 42
        ```

        Attributes:
            values (dict[str, Any]): A mapping of attribute names to their mocked values or callables.

        Use Case:
            - Designed for mocking Ascender Framework services or injectables in testing scenarios.
            - Can also be used for lightweight mocking in any Python context.
        """
        self.values = values

    def _as_object(self, object_name: str, base_type: type[T] | None = None) -> object | T:
        mock_class = type(object_name, (base_type,) if base_type else (), {})
        for key, value in self.values.items():
            setattr(mock_class, key, value)
        
        instance = mock_class()
        
        if not hasattr(instance, "__mock_name__"):
            setattr(instance, "__mock_name__", object_name)
        if not hasattr(instance, "__mock_values__"):
            setattr(instance, "__mock_values__", self.values)

        return instance


    def __getattr__(self, item):
        return self.values.get(item)