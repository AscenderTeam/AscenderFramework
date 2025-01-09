"""
Core module initializer.

Exposes key components of the framework's core functionalities, 
including database entities, engines, dependency injection, and CLI utilities.
"""

from .struct.controller import Controller
from .struct.routes import Get, Post, Put, Patch, Delete
from .di.interface.provider import Provider

from .di.inject import Inject
from .di.injectfn import inject
from .struct.module import AscModule
from .services import Service
from .repositories import Repository, IdentityRepository

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
    "IdentityRepository"
]