from abc import abstractmethod
from functools import wraps
from typing import final
from typing import Any, Callable

from fastapi.params import Depends

from ascender.core.registries.service import ServiceRegistry
from ascender.core.struct.module_ref import AscModuleRef


class ParamGuard:
    __di_module__: AscModuleRef = None
    __declaration_type__: str = "guard"
    
    @abstractmethod
    def __init__(self):
        ...
    
    @abstractmethod
    def __post_init__(self):
        ...

    @final
    def handle_di(self):
        if not self.__di_module__:
            params = ServiceRegistry().get_parameters(self.__post_init__)

            return self.__post_init__(**params)
        
        self.__di_module__._injector.inject_factory_def(self.__post_init__)()

    def _define_dependencies(self, executable: Callable[..., None]):
        """
        NOTE: This is an internal method, don't call it if you are using this class in your code.
        Using it outside of it's purpose is prohibited
        """
        from inspect import signature, Parameter
        
        # NOTE: Currently, decorator fetches and recognizes as param dependency only methods which will end on `_guard` suffix
        methods = [getattr(getattr(self, method), "_name", method) for method in dir(self) if callable(getattr(self, method)) and method.endswith('_guard')]
        # WARN: Signature of executable being changed
        sig = signature(executable)
        new_parameters = []

        for name, param in sig.parameters.items():
            if name + "_guard" in methods and param.default == Parameter.empty:
                new_parameters.append(
                    Parameter(name, param.kind, annotation=param.annotation, default=Depends(getattr(self, f"{name}_guard"))))
            else:
                new_parameters.append(param)


        new_sig = sig.replace(parameters=new_parameters)
        executable.__signature__ = new_sig

        return executable
    
    def __call__(self, executable: Callable[..., Any]):
        # NOTE: This function allows dependency injection on the guard only when it will be called
        _updatedfunc = self._define_dependencies(executable)
        
        setattr(_updatedfunc, "_dependencies", [*getattr(executable, "_dependencies", []), Depends(self.handle_di)])

        @wraps(executable)
        async def wrapper(*args, **kwargs):
            return await _updatedfunc(*args, **kwargs)

        return wrapper