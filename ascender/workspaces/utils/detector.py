import os
from pathlib import Path
from typing import Optional, Tuple


def find_upwards(
    filename: str,
    start_path: Optional[str] = None,
    max_depth: Optional[int] = None,
) -> Optional[Path]:
    """
    Search upwards from start_path (or CWD) for a specific filename.

    Args:
        filename: The file to look for at each level.
        start_path: Directory to start from. Defaults to CWD.
        max_depth: Maximum number of levels to climb. None means search
                   all the way to the filesystem root.

    Returns:
        Path to the file if found within the allowed depth, otherwise None.
    """
    current = Path(start_path or os.getcwd()).resolve()
    depth = 0

    while True:
        target = current / filename
        if target.exists():
            return target

        if max_depth is not None and depth >= max_depth:
            break

        parent = current.parent
        if parent == current:
            break

        current = parent
        depth += 1

    return None


def find_workspace_root(
    start_path: Optional[str] = None,
    max_depth: Optional[int] = 10,
) -> Optional[Path]:
    """
    Search upwards for a directory containing 'workspace.json'.
    Returns the Path to that directory.

    Args:
        start_path: Directory to start from. Defaults to CWD.
        max_depth: How many levels up to search. Defaults to 10, which covers
                   deeply nested project subdirs without climbing past the user's
                   home directory in typical setups. Pass None for no limit.
    """
    path = find_upwards("workspace.json", start_path, max_depth=max_depth)
    return path.parent if path else None


def detect_workspace_files(
    start_path: Optional[str] = None,
) -> Tuple[Optional[Path], Optional[Path]]:
    """
    Detects workspace.json and main.py by searching upwards.
    Returns a tuple of (workspace_json_path, main_py_path).
    """
    workspace_json = find_upwards("workspace.json", start_path)
    main_py = find_upwards("main.py", start_path)

    return workspace_json, main_py


def get_workspace_context(start_path: Optional[str] = None):
    """
    Returns a dictionary with workspace paths and root.
    """
    w_json, m_py = detect_workspace_files(start_path)
    root = w_json.parent if w_json else (m_py.parent if m_py else None)

    return {
        "root": root,
        "workspace_json": w_json,
        "main_py": m_py,
        "is_valid": w_json is not None
    }
