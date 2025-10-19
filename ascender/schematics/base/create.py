from abc import ABC, abstractmethod
from typing import Any
from jinja2 import Template


class SchematicsCreator(ABC):
    
    @abstractmethod
    def load_template(self):
        ...
    
    @abstractmethod
    def post_processing(self):
        ...
    
    @abstractmethod
    def process_template(self, post_processing: dict[str, Any], template: Template):
        ...
    
    @abstractmethod
    def invoke(self):
        ...