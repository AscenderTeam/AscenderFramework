from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar, final

if TYPE_CHECKING:
    from ascender.core.application import Application


class AbstractModule(ABC):

    @abstractmethod
    def __init__(self):
        """This constructor must be implemented by the subclass."""
        ...
    
    def on_module_init(self):
        ...
    
    def on_application_bootstrap(self, application: "Application"):
        ...
    
    def on_application_shutdown(self, application: "Application"):
        ...
