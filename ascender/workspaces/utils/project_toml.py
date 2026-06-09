import os
from pathlib import Path
from typing import Any, Dict, Optional

import tomlkit
from tomlkit.exceptions import TOMLKitError


def detect_toml(path: Optional[str | Path] = None) -> Optional[Path]:
    """
    Checks for 'pyproject.toml' in the specified directory path.
    If path is None, checks the current working directory.
    """
    base_path = Path(path or os.getcwd()).resolve()
    target = base_path / "pyproject.toml"

    return target if target.exists() else None


def parse_toml(path: Optional[Path | str] = None) -> Optional[Dict[str, Any]]:
    """
    Parses a TOML file. If path is None, it tries to detect it in the CWD.
    """
    if path is None:
        path = detect_toml()

    if path and path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return tomlkit.parse(f.read())
        except (TOMLKitError, OSError):
            return None
    return None


def dict_to_toml(data: Dict[str, Any]) -> str:
    """
    Converts a dictionary to a TOML string.
    """
    return tomlkit.dumps(data)


def save_toml(path: Path, data: Dict[str, Any]) -> bool:
    """
    Saves a dictionary as a TOML file.
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(dict_to_toml(data))
        return True
    except OSError:
        return False
