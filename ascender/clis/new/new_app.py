import click
from ascender.clis.new.new_service import NewService
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import BaseCLI
from ascender.core.cli.models import OptionCMD
from ascender.core.database.types.orm_enum import ORMEnum


class NewCLI(BaseCLI):
    project_name: str = OptionCMD("--name", "--project-name", "-n", required=True, ctype=str)
    orm_mode: str = OptionCMD("--orm-mode", "-om", default="sqlalchemy", 
                              required=False, ctype=click.Choice(["tortoise", "sqlalchemy"]))
    standalone: bool = OptionCMD("--no-standalone", default=False, is_flag=True, required=False)

    def __init__(self, new_service: NewService):
        self.new_service = new_service

    def callback(self, ctx: ContextApplication):
        return self.new_service.initialize_project(ctx, self.project_name, ORMEnum(self.orm_mode), self.standalone)