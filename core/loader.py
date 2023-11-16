import os
from typing import List
from fastapi import FastAPI
from importlib import import_module

from core.types import Controller, ControllerModule



class Loader:
    
    _active_controllers: list[object] = []

    def __init__(self, app: FastAPI, controllers: List[Controller]) -> None:
        self._app = app
        self._controllers = controllers

    def get_controllers(self, controller: Controller):
        return os.listdir(controller['base_path'])
    
    def _check_for_recursive_controllers(self, single_controller: str):
        dirs = os.listdir(single_controller)

        for obj in dirs:
            if os.path.isdir(obj) and os.path.isfile(f'{single_controller}/{obj}/endpoints.py'):
                controller: Controller = {
                    'name': obj,
                    'base_path': f'{single_controller}',
                    'initialize_all_controllers': True,
                }
                self._controllers.append(controller)
                self.load_controller(obj, recursive=False)

    def load_controller(self, controller_name: str, exclude: List[str] = [], recursive: bool = True):
        controller: Controller | None = next((controller for controller in self._controllers if controller['name'] == controller_name), None)

        if not controller:
            return None

        controllers: list[str] = self.get_controllers(controller)

        for mvc in controllers:
            if mvc in exclude:
                continue
            # path: controller/
            if not os.path.isdir(f"{controller['base_path']}/{mvc}"):
                continue
            namespace_path = f"{controller['base_path']}.{mvc}"
            
            # Get controller's endpoints.py
            if os.path.isfile(f"{controller['base_path']}/{mvc}/endpoints.py"):
                module = import_module(f"{namespace_path}.endpoints")
                
                if not module.setup:
                    continue

                prefix = f"/{mvc}"
                router_name = " ".join(mvc.capitalize().split("_"))
                controller_module = self.load_module(module.setup())
                self._active_controllers.append(controller_module)
                
                self._app.include_router(controller_module.router, prefix=prefix, tags=[router_name])

                if recursive:
                    self._check_for_recursive_controllers(f"{controller['base_path']}/{mvc}")
        
    def load_module(self, setup: ControllerModule):
        controller = setup.get('controller')
        services = setup.get('services', {})
        repository = setup.get('repository', None)
        repository_entities = setup.get('repository_entities', {})

        if repository is not None:
            repository = repository(**repository_entities)
        
        service_instances = {}
        for key, service in services.items():
            service._loader = self
            service_instances[key+"_service"] = service(repository=repository)

        return controller(**service_instances)
    
    def load_all_controllers(self, recursive: bool = True):
        """
        ## Load All Controllers

        This method loads all the controllers that are currently registered  as controller
        This means that if controller has `endpoints.py` or `routes.py` it will load it into FastAPI applciation

        Args:
            recursive (bool, optional): Determine whether it should load subdirectories of `controller` like directory. Defaults to True.
        """
        for controller in self._controllers:
            self.load_controller(controller['name'], recursive=recursive)
        
        self.initialize_dependencies()
    
    def initialize_dependencies(self):
        """
        ## Initialize dependencies

        Runs __mounted__ method to initialize all dependencies
        """
        for controller in self._active_controllers:
            if hasattr(controller, 'dependencies'):
                dependencies = getattr(controller, 'dependencies')
                dependencies.__mounted__()
    
    def register_controller(self, controller: Controller):
        """
        ## Register controller

        Registers a new controller, after it will be loaded with funciton `load_all_controllers`
        """
        self._controllers.append(controller)
    