import os

def path_to_namespace(path: str, base_dir: str | None = None):
    """
    Converts a file system path to a Python package namespace.

    Args:
        path (str): The file system path.
        base_dir (str, optional): The base directory to exclude from the namespace. Defaults to None.

    Returns:
        str: The Python package namespace.
    """
    # Normalize the path
    normalized_path = os.path.normpath(path)

    if base_dir:
        base_dir = os.path.normpath(base_dir)
        if normalized_path.startswith(base_dir):
            normalized_path = normalized_path[len(base_dir) + 1 :]  # +1 to remove the separator

    namespace = os.path.splitext(normalized_path)[0].replace(os.path.sep, ".")

    return namespace