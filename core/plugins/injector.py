from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, Optional

if TYPE_CHECKING:
    from core.plugins.plugin_loader import PluginLoader


class PluginInjector:
    def __init__(self, loader: PluginLoader) -> None:
        self.__loader = loader
    
    def inject_mvc(self, component_type: Literal["repository", "controller", "service"],
                   name: str, data: dict[str, Any]):
        
        if not self.__loader._mvc_injectors.get(f"{name}.{component_type}", None):
            self.__loader._mvc_injectors[f"{name}.{component_type}"] = data
            return
        
        self.__loader._mvc_injectors[f"{name}.{component_type}"] = data