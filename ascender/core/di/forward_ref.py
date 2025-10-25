from typing import TYPE_CHECKING, Any, Literal, cast

from ascender.core.errors.scope_error import AscenderScopeError

if TYPE_CHECKING:
    from ascender.core.di.injector import AscenderInjector
    from ascender.core.struct.module_ref import AscModuleRef


class DependencyForwardRef:
    _cached_name: str | None
    
    def __init__(self, injection_scope: type["AscModuleRef"] | Literal["root"] | "AscenderInjector", token: type | str) -> None:
        self.token = token
        self.injection_scope = injection_scope
        self._cached_name = None

    def __set_name__(self, owner, name):
        # self-destruction attribute name
        self._cached_name = name

    def _resolve(self):
        if self.injection_scope == "root":
            from ascender.core.applications.root_injector import RootInjector
            root_injector = RootInjector().injector
            
            if not root_injector:
                raise AscenderScopeError(
                    f"inject({self.token.__name__ if isinstance(self.token, type) else self.token}) called outside Ascender Framework scope.\n"
                    "Possible cause: import-time execution before Application and DI (Dependency Injection) Module initialized."
                )
            
            return root_injector.get(self.token)
        
        if hasattr(self.injection_scope, "_injector"):
            scope_injector = cast(type[AscModuleRef], self.injection_scope)._injector

            if not scope_injector:
                raise AscenderScopeError(
                    f"inject({self.token.__name__ if isinstance(self.token, type) else self.token}) called outside Ascender Framework scope.\n"
                    "Possible cause: import-time execution before Application and DI (Dependency Injection) Module initialized."
                )

            return scope_injector.get(self.token)
        
        ascender_injector = cast("AscenderInjector", self.injection_scope)
        
        return ascender_injector.get(self.token)
    
    def __get__(self, obj: object, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        
        instance = self._resolve()
        setattr(obj, cast(str, self._cached_name), instance)

        return instance