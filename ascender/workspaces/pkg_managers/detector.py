from pathlib import Path

from ascender.workspaces.utils.project_toml import parse_toml

from .base import BasePackageManager
from .poetry import PoetryPackageManager
from .uv import UVPackageManager


def detect_package_manager(project_dir: Path) -> BasePackageManager:
    """
    Auto-detects the package manager used in the given project directory.

    Detection order:
    1. Lock file presence (uv.lock → UV, poetry.lock → Poetry)
    2. pyproject.toml tool sections ([tool.uv] → UV, [tool.poetry] → Poetry)
    3. Falls back to Poetry if nothing is found.
    """
    if (project_dir / "uv.lock").exists():
        return UVPackageManager()

    if (project_dir / "poetry.lock").exists():
        return PoetryPackageManager()

    toml = parse_toml(project_dir / "pyproject.toml")
    if toml:
        tool = toml.get("tool", {})
        if "uv" in tool:
            return UVPackageManager()
        if "poetry" in tool:
            return PoetryPackageManager()

    return PoetryPackageManager()
