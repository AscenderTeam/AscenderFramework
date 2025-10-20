"""
Core module initializer.

Exposes key components of the framework's core functionalities, 
including database entities, engines, dependency injection, and CLI utilities.
"""

from .struct.controller import Controller
from .struct.controller_hook import ControllerDecoratorHook
from .struct.routes import Get, Post, Put, Patch, Delete
from .di.interface.provider import Provider

from .di.inject import Inject
from .di.injectfn import inject
from .di.abc.base_injector import Injector
from .di.test_injector import TestInjector
from .struct.module import AscModule
from .services import Service
from .repositories import Repository, IdentityRepository

from .database import AppDBContext

from .applications.application import Application

from . import cli_engine

__all__ = [
    "Injector",
    "TestInjector",
    "Application",
    "AppDBContext",
    "Provider",
    "Inject",
    "inject",
    "AscModule",
    "Controller", 
    "Get", 
    "Post", 
    "Put", 
    "Patch", 
    "Delete",
    "Service",
    "Repository",
    "IdentityRepository",
    "ControllerDecoratorHook",
    *cli_engine.__all__
] # type: ignore