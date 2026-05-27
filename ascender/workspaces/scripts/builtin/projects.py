from argparse import REMAINDER
from typing import Annotated, Literal, cast

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ascender.core.cli_engine import (
    BooleanParameter,
    Command,
    GenericCLI,
    Handler,
    Parameter,
)
from ascender.schematics.workspace.create import WorkspaceCreator
from ascender.workspaces.projects.manager import WorkspaceProjectManager

console = Console()


def _error(message: str) -> None:
    console.print(
        Panel(
            f"[red]{message}[/red]",
            title="[bold red] Error[/bold red]",
            border_style="red",
            padding=(0, 1),
        )
    )


def _success(title: str, message: str) -> None:
    console.print(
        Panel(
            message,
            title=f"[bold green] {title}[/bold green]",
            border_style="green",
            padding=(0, 1),
        )
    )


@Command(name="workspaces", description="Manage your workspace projects")
class WorkspaceCLI(GenericCLI):
    def __init__(self, projects_manager: WorkspaceProjectManager) -> None:
        super().__init__()
        self.projects_manager = projects_manager

    @Handler("init", description="Initialize a new workspace")
    def init_workspace(
        self,
        name: str,
        path: Annotated[str, Parameter("", names=["--path"])],
    ) -> None:
        console.print(
            Panel(
                "[dim]Initializing a new workspace.[/dim]",
                title="[bold yellow]Workspace[/bold yellow]",
                border_style="yellow",
            )
        )
        workspace_creator = WorkspaceCreator(name=name, path=path if path else None)

        try:
            workspace_creator.invoke()
        except Exception as e:
            _error(str(e))
            return

        _success("Workspace", f"Workspace '{name}' has been successfully created.")

    @Handler("list", description="List all projects in your workspace")
    def list_projects(self) -> None:
        try:
            projects = self.projects_manager.list()
        except Exception as e:
            _error(str(e))
            return

        if not projects:
            console.print(
                Panel(
                    "[dim]No projects have been added to this workspace yet.[/dim]",
                    title="[bold yellow]Workspace Projects[/bold yellow]",
                    border_style="yellow",
                )
            )
            return

        table = Table(
            border_style="bright_blue",
            header_style="bold bright_blue",
            show_lines=True,
            expand=False,
        )
        table.add_column("Name", style="bold white", no_wrap=True)
        table.add_column("Description", style="dim", max_width=48)
        table.add_column("Version", justify="center", style="cyan", no_wrap=True)
        table.add_column("Package", justify="center", no_wrap=True)

        for project in projects:
            is_pkg = (
                Text("✓", style="bold green")
                if project.get("is_package")
                else Text("—", style="dim")
            )
            table.add_row(
                project.get("name") or Text("—", style="dim"),
                project.get("description") or Text("—", style="dim"),
                project.get("version") or Text("—", style="dim"),
                is_pkg,
            )

        console.print()
        console.print(
            Panel(
                table,
                title=f"[bold bright_blue]Workspace Projects[/bold bright_blue]  [dim]({len(projects)} total)[/dim]",
                border_style="bright_blue",
                padding=(0, 1),
            )
        )
        console.print()

    @Handler("create", description="Create a new project in your workspace")
    def create(
        self,
        project: str,
        name: Annotated[str, Parameter(names=["--name"], description="Project name")],
        type: Annotated[
            str,
            Parameter(
                "ascender",
                names=["--type", "-t"],
                description="Project type (ascender or package)",
            ),
        ],
        description: Annotated[
            str,
            Parameter(
                "",
                names=["--description"],
                description="Short description of the project",
            ),
        ],
        orm: Annotated[
            str,
            Parameter(
                names=["--orm", "-o"],
                description="ORM mode to use (e.g., 'sqlalchemy', 'tortoise')",
                default="sqlalchemy",
            ),
        ],
        standalone: Annotated[
            bool,
            BooleanParameter(
                flags=["--no-standalone", "--standalone"],
                description="Whether to create a standalone project",
            ),
        ],
    ) -> None:
        options = []
        if description:
            options += ["--description", description]
        if orm:
            options += ["--orm", orm]
        if standalone:
            options += ["--standalone"]

        console.print(
            f"\n[bold bright_blue] Creating[/bold bright_blue] [bold white]{name}[/bold white] "
            f"[dim]({type})[/dim]\n"
        )

        try:
            self.projects_manager.create(
                project=project,
                name=name,
                mode=cast(Literal["ascender", "package"], type),
                options=options,
            )
        except Exception as e:
            _error(str(e))
            return

        _success(
            "Project Created",
            f"[bold white]{name}[/bold white] is ready.\n"
            f"[dim]type  [/dim][cyan]{type}[/cyan]",
        )
        console.print()

    @Handler(
        "link",
        description=(
            "Link an already existing project directory to the workspace. "
            "The directory must contain a pyproject.toml."
        ),
    )
    def link(
        self,
        project: str,
        name: Annotated[
            str,
            Parameter(
                "{name}",
                names=["--name"],
                description="Alias for the project in workspace.json",
            ),
        ],
    ) -> None:
        with console.status(
            f"[bold bright_blue]Linking[/bold bright_blue] [white]{project}[/white][dim] → {name}[/dim]..."
        ):
            try:
                self.projects_manager.link(project=project, name=name)
            except Exception as e:
                _error(str(e))
                return

        _success(
            "Project Linked",
            f"[bold white]{project}[/bold white] is now part of this workspace as [cyan]{name}[/cyan].",
        )
        console.print()

    @Handler(
        "install",
        description=(
            "Install a workspace project into the current project as a dependency. "
            "Run this from inside the target project's directory."
        ),
    )
    def install(
        self,
        project: str,
        _extra: list[str] = Parameter(
            default_factory=list,
            names=["extra"],
            description="Additional arguments to pass to the package manager.",
            nargs=REMAINDER,
        ),
    ) -> None:
        console.print(
            f"\n[bold bright_blue] Installing[/bold bright_blue] [bold white]{project}[/bold white] "
            f"[dim]into current project...[/dim]\n"
        )

        try:
            self.projects_manager.install(source=project)
        except Exception as e:
            _error(str(e))
            return

        _success(
            "Installed",
            f"[bold white]{project}[/bold white] has been added as a dependency.\n"
            f"[dim]Path is stored as a relative reference in pyproject.toml.[/dim]",
        )
        console.print()
