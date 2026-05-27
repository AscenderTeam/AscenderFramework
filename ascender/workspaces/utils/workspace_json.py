import json
from pathlib import Path
from typing import Union, Optional, Any

from ascender.workspaces._configs.workspace import WorkspaceConfigs
from .detector import find_upwards


def load_workspace_json(path: Optional[Path] = None) -> Optional[dict]:
    """
    Loads workspace.json content as a dictionary.
    If path is None, it tries to find it upwards.
    """
    if path is None:
        path = find_upwards("workspace.json")
        
    if path and path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def get_workspace_config(path: Optional[Path] = None) -> Optional[WorkspaceConfigs]:
    """
    Loads workspace.json and returns a validated WorkspaceConfigs object.
    Searches upwards if path is not provided. Returns None if not found or invalid.
    """
    if path is None:
        path = find_upwards("workspace.json")

    if path and path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return WorkspaceConfigs.model_validate_json(f.read())
        except Exception:
            return None
    return None


def find_workspace_config_path() -> Optional[Path]:
    """Returns the path to workspace.json by searching upwards, or None."""
    return find_upwards("workspace.json")


def save_workspace_json(data: Union[dict, WorkspaceConfigs], path: Optional[Path] = None) -> Path:
    """
    Saves WorkspaceConfigs or a dict to workspace.json.
    Searches upwards for workspace.json if path is not provided.
    Raises FileNotFoundError if workspace.json cannot be found.
    """
    target_path = path
    if target_path is None:
        target_path = find_upwards("workspace.json")
        
    if target_path is None:
        raise FileNotFoundError("Could not find 'workspace.json' in this directory or any parent directory.")

    if isinstance(data, WorkspaceConfigs):
        # Use pydantic's model_dump_json for proper serialization
        content = data.model_dump_json(indent=4)
    else:
        content = json.dumps(data, indent=4)
        
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return target_path
