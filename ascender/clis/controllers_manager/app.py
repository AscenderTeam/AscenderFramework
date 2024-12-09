from typing import TYPE_CHECKING, Literal

import click
from ascender.core.cli import GenericCLI
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import console_command
from ascender.core.cli.models import OptionCMD
from ascender.clis.controllers_manager.service import ControllerService
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.core.utils.sockets import ApplicationContext

if TYPE_CHECKING:
    from ascender.core.application import Application, ServiceRegistry

class ControllersManagerCLI(GenericCLI):
    app_name: str = "ctrls"
    help: str | None = "Easily manage controllers with this powerful CLI tool"

    def __init__(self, _application: "Application", _sr: "ServiceRegistry"):
        super().__init__(_application, _sr)
        self._sr.add_singletone(ControllerService, ControllerService(self._sr))

    @console_command(name="new")
    def new_controller(self, ctx: ContextApplication, 
                       controller_service: ControllerService,
                       controller_name: str = OptionCMD("--name", "-n"),
                       controller_dir: str = OptionCMD("--dir", "-d", default="controllers",
                                                       required=False)):
        controller_service.build_basic_controller(ctx, controller_name,
                                                  controller_dir.removeprefix("/").removesuffix("/"))
    
    @console_command(name="identity")
    def new_auth_controller(self, ctx: ApplicationContext,
                            controller_service: ControllerService,
                            entity_module: str = OptionCMD("--entity-module", "-em", default="user.UserEntity", required=False),
                            orm_mode: Literal["tortoise", "sqlalchemy"] = OptionCMD("--orm-mode", "-om", ctype=click.Choice(["tortoise", "sqlalchemy"]),
                                                                                    required=False, default="tortoise"),
                            controller_name: str = OptionCMD("--name", "-n", default="auth",
                                                             required=False),
                            controller_dir: str = OptionCMD("--dir", "-d", default="controllers",
                                                       required=False)):
        controller_service.build_auth_controller(ctx, controller_name, controller_dir, ORMEnum(orm_mode), entity_module)