import os
import subprocess
from pathlib import Path
from typing import Literal

from ascender.common import Injectable
from ascender.workspaces._configs.workspace_project import WorkspaceProject
from ascender.workspaces.pkg_managers import detect_package_manager
from ascender.workspaces.utils.detector import find_workspace_root
from ascender.workspaces.utils.project_toml import parse_toml
from ascender.workspaces.utils.workspace_json import (
    find_workspace_config_path,
    get_workspace_config,
    save_workspace_json,
)


@Injectable(provided_in=None)
class WorkspaceProjectManager:
    def __init__(self) -> None: ...

    @property
    def wconfig(self):
        path = find_workspace_config_path()
        if path is None:
            raise Exception(
                "Could not find workspace.json — are you inside a workspace directory?"
            )
        config = get_workspace_config(path)
        if config is None:
            raise Exception(
                f"Found workspace.json at '{path}' but it appears invalid or corrupted."
            )
        return config

    def list(self):
        """
        Lists all projects defined in `workspace.json`
        Additionally, it also inspects `pyproject.toml` and prevoides basic information about project e.g. (description, version and is package boolean)
        """
        projects = self.wconfig.projects

        result = []

        for project in projects:
            project_dir = Path(project if isinstance(project, str) else project.path)
            toml = parse_toml(project_dir / "pyproject.toml")

            if not toml:
                continue

            poetry = toml.get("tool", {}).get("poetry", {})
            result.append(
                {
                    "name": toml.get("project", {}).get("name") or poetry.get("name"),
                    "description": toml.get("project", {}).get("description")
                    or poetry.get("description"),
                    "version": poetry.get("version")
                    or toml.get("project", {}).get("version"),
                    "is_package": bool(poetry.get("packages")),
                }
            )

        return result

    def create(
        self, project: str, name: str, mode: Literal["ascender", "package"], **kwargs
    ):
        """
        Creates a new project in the workspace.

        Args:
            name (str): Name of the new project (it can be relative path to the workspace root, in that case a subdirectory will be created if it doesn't exist by path given in this argument).
            mode (Literal["ascender", "package"]): Type of the project (ascender framework project or a simple poetry package with package mode on).
        """
        workspace_dir = find_workspace_root()
        if not workspace_dir:
            raise Exception(
                "Not an ascender framework workspace, couldn't find workspace config file!"
            )

        options = kwargs.get("options", [])
        if isinstance(options, str):
            options = [options] if options else []

        path = project.split("/")

        if len(path) > 1:
            for i in range(len(path)):
                if not path[i]:
                    continue

                if not Path(workspace_dir, *path[: i + 1]).exists():
                    Path(workspace_dir, *path[: i + 1]).mkdir()

        if mode == "ascender":
            project_parent = (
                Path(workspace_dir, *path[:-1])
                if len(path) > 1
                else Path(workspace_dir)
            )
            subprocess.call(
                ["ascender", "new", "--name", path[-1], *options],
                cwd=project_parent,
            )

        if mode == "package":
            package_path = Path(workspace_dir, *path)
            package_path.mkdir(exist_ok=True)

            subprocess.call(["poetry", "init"], cwd=package_path)

            # Create subdir for library
            lib_path = Path(package_path, "src", name)
            lib_path.mkdir(parents=True, exist_ok=True)

            # Create mainfile
            main_path = Path(lib_path, "__init__.py")
            main_path.touch()

            # Create subdir for tests
            test_path = Path(package_path, "tests", name)
            test_path.mkdir(parents=True, exist_ok=True)

        config = self.wconfig
        if path[-1] == name:
            config.projects.append(os.path.join(*path))
        else:
            config.projects.append(
                WorkspaceProject(name=name, path=os.path.join(*path))
            )

        save_workspace_json(config)

    def install(self, source: str, target: str | None = None):
        """
        Installs a workspace project into another project as a dependency using `poetry add`.
        The path stored in the target's `pyproject.toml` is always relative — Poetry
        tends to write absolute paths even when given a relative one, so this method
        patches the file afterwards if needed.

        Args:
            source (str): Name of the workspace project to install as a dependency.
            target (str | None): Name of the workspace project to install into.
                                 If omitted, the current working directory is used as the target.
        """
        workspace_dir = find_workspace_root()
        if workspace_dir is None:
            raise Exception(
                "Not an ascender framework workspace, couldn't find workspace config file!"
            )

        source_path = self._resolve_project_path(source, workspace_dir)
        target_path = (
            Path.cwd()
            if target is None
            else self._resolve_project_path(target, workspace_dir)
        )

        if not (source_path / "pyproject.toml").exists():
            raise Exception(f"Source project '{source}' doesn't have a pyproject.toml!")

        if not (target_path / "pyproject.toml").exists():
            raise Exception(
                f"Target project at '{target_path}' doesn't have a pyproject.toml!"
            )

        pkg_manager = detect_package_manager(target_path)
        pkg_manager.add(source_path, target_path)

    def _resolve_project_path(self, name: str, workspace_dir: Path) -> Path:
        for project in self.wconfig.projects:
            if isinstance(project, str):
                if Path(project).name == name or project == name:
                    return Path(workspace_dir, project)
            else:
                if project.name == name:
                    return Path(workspace_dir, project.path)
        raise Exception(f"Project '{name}' not found in workspace!")

    def link(self, project: str, name: str):
        """
        If there is any directory in the workspace by the given name in `project` parameter that contains `pyproject.toml` file,
        it will be added to `workspace.json` and counted as a project.

        Args:
            project (str): Name of the directory or relative path to directory from the workspace's root path.
            name (str): Name of the project, which will be added to `workspace.json`

        NOTE: Name can be different than file name, and that means it is aliased or renamed in workspace.json manifest, but that changes nothing!
        """
        workspace_dir = find_workspace_root()
        if not workspace_dir:
            raise Exception(
                "Not an ascender framework workspace, couldn't find workspace config file!"
            )

        project_path = Path(workspace_dir, project)

        if not project_path.exists():
            raise Exception(f"Directory '{project_path}' doesn't exist!")

        if not Path(project_path, "pyproject.toml").exists():
            raise Exception(
                f"Directory '{project_path}' doesn't contain 'pyproject.toml' file!"
            )

        for existing in self.wconfig.projects:
            existing_name = existing if isinstance(existing, str) else existing.name
            if existing_name == name:
                raise Exception(f"Project with name '{name}' already exists!")

        config = self.wconfig
        config.projects.append(WorkspaceProject(name=name, path=project))
        save_workspace_json(config)
