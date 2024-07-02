from abc import ABC, abstractmethod
from typing import Any


class ControllerBuilder(ABC):
    name: str
    controller_dir: str

    def __init__(self, name: str, controller_dir: str) -> None:
        self.name = name
        self.controller_dir = controller_dir
    
    @abstractmethod
    def prepare_placeholders(self) -> dict[str, str]:
        ...

    @abstractmethod
    def build(self, extra_dirs: bool) -> dict[str, str]:
        ...
    
    def __call__(self, extra_dirs: bool = False):
        return self.build(extra_dirs)