import importlib
from typing import Sequence

from ascender.core._config.asc_config import _AscenderConfig
from ascender.core._config.interface.runtime import OverrideConfig
from ascender.core.di.injector import AscenderInjector
from ascender.core.di.interface.provider import Provider


def create_injector(
    providers: Sequence[Provider],
    parent: AscenderInjector | None = None
):
    config = _AscenderConfig()
    environment = config.get_environment()
    
    overrides = environment.dependency_injection.overrides if environment.dependency_injection else OverrideConfig(enabled=False, injector="ascender.core.di.injector.AscenderInjector")
    
    if overrides.enabled:
        path = overrides.injector or "ascender.core.di.injector.AscenderInjector"
        
        mod_name, cls_name = path.rsplit(".", 1)
        mod = importlib.import_module(mod_name)
        
        injector_class = getattr(mod, cls_name)
        
        if not injector_class or not issubclass(injector_class, AscenderInjector):
            raise ValueError(f"Injector {cls_name} not found in module {mod_name} or is not a subclass of AscenderInjector." \
                            f" Please check your configuration in `ascender.json`.")

        return injector_class(providers, parent=parent)

    return AscenderInjector(providers, parent=parent)