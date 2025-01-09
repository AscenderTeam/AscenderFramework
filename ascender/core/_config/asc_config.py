import os
from typing import Self

from pydantic import ValidationError

from ascender.core.errors.config_error import AscenderConfigError

from .interface.main import AscenderConfig


class _AscenderConfig:
    _instance: Self | None = None
    config: AscenderConfig
    is_built: bool = False

    def __new__(cls) -> Self:
        if not cls._instance:
            cls._instance = super(_AscenderConfig, cls).__new__(cls)
            cls._instance.load_config()
        
        return cls._instance
    
    def get_environment(self):
        if not self.is_built:
            return self.config.environment.environments[self.config.environment.default]
        
        return self.config.environment.environments[self.config.build.target]

    def load_config(self):
        if os.getenv("ASC_MODE", "server") == "cli":
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "stub.json")
        else:
            path = os.path.abspath("ascender.json")
        
        if not os.path.exists(path):
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "stub.json")
        
        with open(path, "r") as f:
            try:
                self.config = AscenderConfig.model_validate_json(f.read())
            except ValidationError as e:
                self.handle_validation_err(e)
    
    def handle_validation_err(self, e: ValidationError):
        raise AscenderConfigError(f"ASE_{e.title.upper()}")
    
    def get_version(self):
        return self.config.project.get("version", "0.1.0")