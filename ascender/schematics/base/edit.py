from abc import ABC, abstractmethod
from typing import Any


class SchematicsEditor(ABC):
    
    @abstractmethod
    def load_file(self):
        ...
    
    @abstractmethod
    def regex_processing(self, file_contents: str):
        ...

    @abstractmethod
    def post_processing(self, regex_values: dict[str, Any] | list[Any]):
        ...
    
    @abstractmethod
    def process_file(self, post_processing: dict[str, Any], processed_file_contents: str):
        ...
    
    @abstractmethod
    def invoke(self):
        ...