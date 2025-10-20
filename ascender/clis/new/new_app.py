import click
from ascender.clis.new.new_service import NewService
from ascender.core.cli.application import ContextApplication
from ascender.core.cli.main import BaseCLI
from ascender.core.cli.models import OptionCMD
from ascender.core.cli_engine import Command, BasicCLI, Parameter
from ascender.core.cli_engine.parameters.boolean import BooleanParameter
from ascender.core.database.types.orm_enum import ORMEnum


@Command(name="new", description="Create a new Ascender Framework project.", aliases=["n"], help="Initialize a new Ascender project structure.")
class NewCLI(BasicCLI):
    project_name: str = Parameter(names=["--name", "--project-name", "-n"], description="Name of the new project")
    orm_mode: str = Parameter(names=["--orm", "-o"], description="ORM mode to use (e.g., 'sqlalchemy', 'tortoise')", default="sqlalchemy")
    standalone: bool = BooleanParameter(flags=["--no-standalone", "--standalone"], description="Whether to create a standalone project")
    relpath: str = Parameter(names=["--relpath"], description="Relative path to create the project in", default="{project_name}")

    def __init__(self, new_service: NewService):
        self.new_service = new_service

    def execute(self):
        return self.new_service.initialize_project(self.project_name, self.relpath, ORMEnum(self.orm_mode), self.standalone)