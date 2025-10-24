"""
Core module initializer.

Exposes key components of the framework's core functionalities,
including database entities, engines, dependency injection, and CLI utilities.
"""

from .di.inject import Inject
from .di.injectfn import inject
from .di.interface.provider import Provider
from .repositories import IdentityRepository, Repository
from .services import Service
from .struct.controller import Controller
from .struct.controller_hook import ControllerDecoratorHook
from .struct.module import AscModule
from .struct.routes import Delete, Get, Patch, Post, Put

__all__ = [
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
]
