from typing import cast
from ascender.core.router.interface.route import RouterRoute
from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef


def is_direct_controller(route: RouterRoute):
    if not (controller := route.get("controller", None)):
        return False
    
    return hasattr(controller, "__controller__")


def is_module_controller(route: RouterRoute):
    if not (module := route.get("load_controller", None)):
        return False
    module = module()
    
    return hasattr(module, "__asc_module__") and not hasattr(module, "__controller__")


""":internal:"""
def unwrap_module_controller(module: type[AscModuleRef], target: type[ControllerRef] | None = None):
    controller: type[ControllerRef] | None = None
    if hasattr(module.__asc_module__, "consumers"):
        for consumer in module.__asc_module__.consumers: # type: ignore (behaviour of type checker is unpredictable here)
            if target is not None:
                if consumer is target and consumer in module.__asc_module__.exports:
                    controller = consumer
                    break

                continue

            if hasattr(consumer, "__controller__") and consumer in module.__asc_module__.exports:
                controller = consumer
                break
        
        if not controller:
            raise ValueError(f"AscModule {module.__name__} doesn't have any controllers declared!")
        
        return module, controller
    
    raise RuntimeError(f"{module.__name__} is not recognized and allowed `AscModule`!")