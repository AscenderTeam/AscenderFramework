from core.types import ControllerModule
from importlib import import_module
from os import PathLike

import os
import inspect

from settings import BASE_PATH



class RepositoryCreator:
    def __init__(self, controller: str, base_path: PathLike = "controllers/") -> None:
        self.base_path = base_path
        self.controller = controller

    def determine_controller(self) -> ControllerModule:
        """
        Find the controller object in the controllers folder
        """
        main_file = f"{self.base_path}/{self.controller}/endpoints.py"
        repository_file = f"{self.base_path}/{self.controller}/repository.py"

        if not os.path.isfile(main_file):
            raise Exception("Controller not found") # TODO: Normal exception handlers
        
        if not os.path.isfile(repository_file):
            raise Exception("Repository file not found")
        
        controller = import_module(f"{self.base_path}.{self.controller}.repository")

        if not controller.setup or not callable(controller.setup):
            raise Exception("Controller setup function not found") # TODO: Normal exception handlers
        
        if not isinstance(controller.setup(), ControllerModule):
            raise Exception("Invalid controller module") # TODO: Normal exception handlers
        
        self.main_file = main_file
        self.repository_file = repository_file

        return controller.setup()
    
    def get_entities(self, controller: ControllerModule) -> list[str]:
        """
        Get the entities from the controller
        """
        entities = controller["repository_entities"]
        if not isinstance(entities, list):
            raise Exception("Invalid entities") # TODO: Normal exception handlers
        
        entities_buffer: dict[str, tuple[str]] = {}

        for entity_key, entity_value in entities.items():
            _keyname = entity_key
            _entity_path = inspect.getfile(entity_value)
            # Format it into import path
            _entity_path = os.path.relpath(_entity_path, start=BASE_PATH)
            _entity_path = _entity_path.removesuffix(".py").replace("/", ".")

            entities_buffer[_keyname] = _entity_path, entity_value.__class__.__name__

        return entities_buffer

    def creator_run(self, repository: ControllerModule) -> list[str]:
        """
        Starts magic process of creating the repository
        """
        _controller = self.determine_controller()
        _entities = self.get_entities(_controller)

        # Open the repository and edit
        with open(self.repository_file, "r") as repository_file:
            repository_files = repository_file.readlines()

        class_start_index = 0
        class_init_index = 0
        class_end_index = len(repository_files) - 1

        # Find the line where to work and append the entities        
        for index, line in enumerate(repository_files):
            if line.find(f"class {repository.__class__.__name__}") != -1:
                class_start_index = index
                continue
            

