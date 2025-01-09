from typing import Any, Literal, TypeVar

from ascender.core.applications.root_injector import RootInjector
from ascender.core.di.interface.consts import RAISE_NOT_FOUND
from ascender.core.errors.scope_error import ScopeError
from ascender.core.struct.module_ref import AscModuleRef


T = TypeVar("T")


def inject(
    token: type[T] | str, 
    fallback: T | Any | None = None,
    *,
    scope: type[AscModuleRef] | Literal["root"] = "root"
) -> T:
    """
    Retrieves an instance of the specified token from the dependency injection system.

    This function is particularly useful for standalone functions or scenarios where
    the injector is not directly accessible, allowing seamless access to dependencies.

    Args:
        token (type[T] | str): The type or name of the token to retrieve from the injector.
        fallback (T | Any | None, optional): The value to return if the token is not found.
            If `None` and the token is not found, the function raises a `RAISE_NOT_FOUND` error.
            Defaults to `None`.
        scope (type[AscModuleRef] | Literal["root"], optional): The scope to search for the token.
            - If "root" (default), the token is retrieved from the `RootInjector`.
            - If a specific `AscModuleRef` type is provided, the token is retrieved from that module's injector.
            Defaults to "root".

    Returns:
        T: The instance of the specified token, or the fallback value if the token is not found
            and `fallback` is provided.

    Raises:
        ScopeError: If the specified scope is invalid or inaccessible.
        RuntimeError: If the specified module scope is not loaded, preventing access to its injector.

    Examples:
    ```
        # Retrieve a token from the root scope
        my_service = inject(MyService)

        # Retrieve a token from a specific module scope
        my_service = inject(MyService, scope=MyModule)

        # Retrieve a token with a fallback value
        my_service = inject("MyService", fallback=default_service)
    ```

    Notes:
        - This function is ideal for use in standalone functions where injectors
          are not directly accessible, such as utility functions or handlers outside
          the main dependency injection context.
        - If the `scope` is a string, it must be "root". Any other string raises a `ScopeError`.
        - If the `scope` is an `AscModuleRef` type, it must be loaded, lazy-loaded modules cannot be accessed unless they are loaded.
          Otherwise, a `RuntimeError` is raised.
    """
    if isinstance(scope, str):
        if scope == "root":
            return RootInjector().existing_injector.get(token, not_found_value=RAISE_NOT_FOUND if not fallback else fallback)
        
        raise ScopeError(f"Unable to access specified `{scope}` scope")
    
    if not hasattr(scope, "__asc_module__"):
        raise ScopeError(f"Unable to access specified `{scope.__name__}` scope")
    
    if not hasattr(scope, "_injector"):
        raise RuntimeError(f"Unable to access scope `{scope.__name__}` due to `NotLoadedModule` error!")
    
    loaded_injector = scope._injector
    return loaded_injector.get(token, not_found_value=RAISE_NOT_FOUND if not fallback else fallback)