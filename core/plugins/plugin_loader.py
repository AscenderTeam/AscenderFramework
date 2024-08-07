from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal
from core.plugins.plugin import Plugin
from core.plugins.plugin_injector import PluginInjector
from core.store.distributor import Distributor
from core.types import ControllerModule
from rich.logging import RichHandler
import logging

from settings import PLUGINS_LOGLEVEL

if TYPE_CHECKING:
    from core.application import Application


class PluginLoader:
    """
    ## Plugin Loader

    The core engine plugin loader is responsible for managing plugins and loading them.
    """
    __plugins: dict[str, Plugin] = {}

    def __init__(self, application: Application) -> None:
        self.application = application
        self.setup_logger()
        
    def setup_logger(self):
        logger = logging.getLogger("ascender-plugins")
        
        # handlers checkup
        if logger.hasHandlers():
            logger.handlers.clear()

        rich_handler = RichHandler(
            rich_tracebacks=True,
            show_time=True,
            markup=True,
        )
        logger.setLevel(PLUGINS_LOGLEVEL)
        # rich_handler.setFormatter(PluginsLoggerFormatter())
        logger.addHandler(rich_handler)
        logger.propagate = False
        self.logger = logger

    def use_plugin(self, plugin: Plugin):
        plugin.logger = self.logger
        plugin.injector = PluginInjector(self.application)
        plugin.install(self.application)
        self.__plugins[plugin.name] = plugin

    def before_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        for _, plugin in self.__plugins.items():
            plugin.before_controller_load(name, instance, configuration)

    def after_controller_load(self, name: str, instance: object, configuration: ControllerModule):
        for _, plugin in self.__plugins.items():
            plugin.after_controller_load(name, instance, configuration)

    def initialize_dependencies(self, active_controllers: list[object]):
        for _, plugin in self.__plugins.items():
            plugin.on_dependency_intialization(active_controllers)
