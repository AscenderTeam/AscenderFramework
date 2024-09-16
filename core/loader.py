from __future__ import annotations
import asyncio
from genericpath import isfile
from inspect import isawaitable, unwrap
import os
from pathlib import Path
from typing import TYPE_CHECKING, List
from fastapi import FastAPI
from importlib import import_module
from core.database.engine import DatabaseEngine
from core.database.orms.sqlalchemy import SQLAlchemyORM
from core.extensions.repositories import IdentityRepository, Repository
from core.extensions.services import Service
from core.plugins.plugin_loader import PluginLoader
from core.sockets import LoadedEndpoints
from core.store.distributor import Distributor
from core.store.storage import BaseStore

from core.types import Controller, ControllerModule

if TYPE_CHECKING:
    from core.application import Application



class Loader:
    
    _active_controllers: list[object] = []

    def __init__(self, app: FastAPI, application: Application, controllers: List[Controller], plugin_loader: PluginLoader) -> None:
        self._app = app
        self._application = application
        self._controllers = controllers
        self._plugin_loader = plugin_loader

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

            if os.path.isfile(f"{controller['base_path']}/{mvc}/.ignore"):
                continue
            
            namespace_path = f"{Path(controller['base_path']).as_posix().replace('/', '.')}.{mvc}"
            
            # Get controller's endpoints.py
            if os.path.isfile(f"{controller['base_path']}/{mvc}/endpoints.py"):
                module = import_module(f"{namespace_path}.endpoints")
                
                if not module.setup:
                    continue
                
                prefix = f"/{mvc}"
                router_name = " ".join(mvc.capitalize().split("_"))
                controller_module = self.load_module(module.setup())
                self._active_controllers.append(controller_module)
                prefix = controller_module._router_prefix + prefix
                self._app.include_router(controller_module.router, prefix=prefix, tags=[router_name])
                
                self._plugin_loader.after_controller_load(controller_module.__class__.__name__, controller_module, module.setup())
                
                if recursive:
                    self._check_for_recursive_controllers(f"{controller['base_path']}/{mvc}")
        
    def load_module(self, setup: ControllerModule):
        controller = setup.get('controller')
        services = setup.get('services', {})
        repository = setup.get('repository', None)
        
        self._plugin_loader.before_controller_load(unwrap(controller).__name__, controller, setup)

        if repository is not None:
            irepository = repository
            repo_args = {}
            db_engine = self._application.service_registry.get_singletone(DatabaseEngine)
            if db_engine and isinstance(db_engine.engine, SQLAlchemyORM):
                repo_args["_context"] = db_engine.generate_context()
            try:
                repository = repository(**repo_args)
            except TypeError as e:
                print(e)
                repository = repository()
            
            self._application.service_registry.add_singletone(irepository, repository)
        
        for key, service in services.items():
            service._loader = self
            self._application.service_registry.add_singletone(service, service(repository=repository))

        parameters = self._application.service_registry.get_parameters(controller.__init__)
        return controller(**parameters)
    
    def load_all_controllers(self, recursive: bool = True):
        """
        ## Load All Controllers

        This method loads all the controllers that are currently registered  as controller
        This means that if controller has `endpoints.py` or `routes.py` it will load it into FastAPI applciation

        Args:
            recursive (bool, optional): Determine whether it should load subdirectories of `controller` like directory. Defaults to True.
        """
        for controller in self._controllers:
            self.load_controller(controller['name'], exclude=controller["exclude_controllers"], recursive=recursive)
    
    def initialize_dependencies(self):
        """
        ## Initialize dependencies

        Features:
        - Runs __mounted__ method to initialize all dependencies
        - Mounts all SocketIO endpoints
        """
        # for controller in self._active_controllers:
        #     if hasattr(controller, 'injectable_services'):
        #         for service in getattr(controller, 'injectable_services'):
        #             if hasattr(service, "__mounted__"):
        #                 if isawaitable(getattr(service, "__mounted__")):
        #                     asyncio.run(getattr(service, "__mounted__")())
        #                     continue
                        
        #                 getattr(service, "__mounted__")()
        for interface, service in self._application.service_registry.singletones.items():
            if isinstance(service, (Service, Repository, IdentityRepository)):
                # print(interface)
                parameters = self._application.service_registry.get_parameters(service)
                for key, value in parameters.items():
                    setattr(service, key, value)
        
        # Initialize dependencies in plugins
        self._plugin_loader.initialize_dependencies(self._active_controllers)

        if not self._application.socketio:
            return
        # SocketIO endpoints
        _endpoints = LoadedEndpoints.endpoints
        _namespaces = set()
        _afterload_endpoints = []

        for endpoint in _endpoints:
            if endpoint['namespace'] == "[ALL]":
                _afterload_endpoints.append(endpoint)
                continue

            _namespaces.add(endpoint['namespace'])
            self._application.socketio.add_event(endpoint['namespace'], endpoint['event'], endpoint['handler'])

        for endpoint in _afterload_endpoints:
            if endpoint['namespace'] == "[ALL]":

                for namespace in list(_namespaces):
                    self._application.socketio.add_event(namespace, endpoint['event'], endpoint['handler'])
                        
                    continue
    
    def register_controller(self, controller: Controller):
        """
        ## Register controller

        Registers a new controller, after it will be loaded with funciton `load_all_controllers`
        """
        self._controllers.append(controller)
    
    def register_store(self, store: str, instance: BaseStore):
        """
        ## Register store

        Registers a new store, after it will be loaded with funciton `load_all_controllers`
        """
        Distributor.register_store(self._app, store, instance)
