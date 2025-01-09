from typing import Any
from ascender.core.applications.root_injector import RootInjector
from ascender.core.di.injector import AscenderInjector
from ascender.core.di.interface.record import ProviderRecord
from ascender.core.struct.controller_ref import ControllerRef
from ascender.core.struct.module_ref import AscModuleRef


def load_module(
    module: type[AscModuleRef],
    _parent: type[AscModuleRef] | type[ControllerRef] | AscenderInjector | None = None
):
    """
    Instantiates and loads `AscModule` and runs it's injector and all imports alive

    Args:
        module (type[AscModuleRef]): Reference to AscModule
    """
    if _parent is None:
        _parent = RootInjector().existing_injector
    
    if not hasattr(module, "__asc_module__"):
        raise ValueError(f"Failed to recognize AscModule in {module.__name__}")
    
    if hasattr(module, "_injector"):
        raise RuntimeError(f"Failed to instantiate already existing module! {module.__name__}")
    
    return module.__asc_module__.create_module(_parent)


def module_import(module: type[AscModuleRef], injector: AscenderInjector):
    """
    Loads an imported @AscModule into the module.

    Args:
        module: The module to load.
        injector: Injector to load module's dependencies into.
    """
    asc_module = module.__asc_module__
    whitelist = module.__asc_module__.consumers

    if not hasattr(module, "_injector"):
        raise RuntimeError(f"Failed to import module {module.__name__} as it was not initialized.")
    for export in asc_module.exports:
        if export in whitelist:
            continue
        
        if hasattr(export, "__asc_module__"):
            if export not in asc_module.imports:
                raise injector.NONE_INJECTOR.get(export)
            
            module_import(export, injector)
            continue
        
        record = module._injector.get_factory_def(export, self_only=True)

        if record:
            if isinstance(record, list):
                injector.dependencies[export].update(set(record))
            
            else:
                injector.dependencies[export].add(record)
        else:
            raise injector.NONE_INJECTOR.get(export)