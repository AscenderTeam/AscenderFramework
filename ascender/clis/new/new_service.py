import os
import subprocess
from time import sleep
from ascender.clis.generator.create_generator_service import CreateGeneratorService
from ascender.common import Injectable
from ascender.core.services import Service
from ascender.core.cli.application import ContextApplication
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.schematics.project.create import ProjectCreator
from ascender.schematics.utilities.case_filters import kebab_case


@Injectable(provided_in="root")
class NewService(Service):

    def __init__(self, create_generator_service: CreateGeneratorService):
        self.create_generator_service = create_generator_service

    def initialize_project(
        self,
        ctx: ContextApplication,
        name: str,
        orm_mode: ORMEnum,
        standalone: bool
    ):
        _path = os.path.abspath(name.strip().replace(" ", ""))

        if os.path.isdir(_path) and os.listdir(_path):
            raise FileExistsError(
                f"Path {_path} is already exists and is not an empty directory")

        # Make dirs if not exists
        os.makedirs(_path, exist_ok=True)

        # Change directory into project dir
        os.chdir(_path)

        while not os.path.exists(_path):
            sleep(1)
        # Initializing Package Manager, Virtual environment & Ascender Framework package
        self.initialize_packages(name)
        project_files = self.create_project_files(_path, orm_mode, standalone)

        for project_file in project_files:
            ctx.console_print(
                f"[green]{project_file['schematic_type']}[/green] {project_file['file_path']} [cyan]({project_file['write_size']} bytes)[/cyan]")

        # Generate crucial controller parts
        self.create_generator_service.generate_controller(
            f"controllers/main", standalone=True, prefix="", suffix="")
        self.create_generator_service.generate_module(
            f"controllers/controllers")

    def initialize_packages(
        self,
        project_name: str
    ):
        # Initialize package manager: Poetry
        # NOTE: Ascender Framework REQUIRES poetry to be included in project
        subprocess.run(
            f"poetry init --name {kebab_case(project_name).lower()} --python \">=3.11,<3.14\" --description \"{project_name}\" --no-interaction",
            check=True,
            shell=True
        )

        # Installing framework within poetry's virtualenv scope and other additional packages
        subprocess.run("poetry config virtualenvs.create true && poetry add ascender-framework", shell=True, check=True)

    def create_project_files(
        self,
        path: os.PathLike | str,
        orm_mode: ORMEnum,
        standalone: bool
    ):
        project_creator = ProjectCreator(path, orm_mode, standalone)

        if not (project_files := project_creator.invoke()):
            raise ValueError("Failed to generate a crucial project file")

        return project_files
