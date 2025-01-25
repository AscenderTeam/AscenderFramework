import os
import PyInstaller.__main__


def obfuscate_project(
    project_name: str,
    output_dir: str,
    source_dir: str,
    hidden_imports: list[str] = [],
    metadata_imports: list[str] = []
):
    """
    Obfuscates a Python project using PyArmor.

    Args:
        project_name (str): The name of the project to obfuscate.
        output_dir (str): The directory where the obfuscated files will be saved.
        source_dir (str): The directory containing the source files to obfuscate.

    Returns:
        str: The absolute path to the obfuscated project's output directory.
    """
    # Resolve absolute paths
    output_dir = os.path.abspath(f"{output_dir}/{project_name}")
    source_dir = os.path.abspath(f"{source_dir}/_build.py")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define additional python-packages & metadatas
    _hidden_imports = [f"--hidden-import={package}" for package in hidden_imports]
    _recursive_metadata = [f"--recursive-copy-metadata={metadata}" for metadata in metadata_imports]

    print(_hidden_imports)
    print(_recursive_metadata)
    # Define PyArmor obfuscation options
    options = [
        source_dir,    # Source directory
        "--onefile",   # Batch everything into one file
        "--noconfirm",
        "--recursive-copy-metadata", "tortoise-orm",
        "--recursive-copy-metadata", "readchar",
        "--recursive-copy-metadata", "sqlalchemy",
        "--hidden-import=pydantic_core",
        "--hidden-import=pydantic.typing",
        "--hidden-import=pydantic",
        "--hidden-import=uvicorn",
        "--add-data", "ascender.json:ascender.json",
        "--distpath", output_dir,
        *_hidden_imports,
        *_recursive_metadata
    ]

    # Run PyArmor obfuscation
    PyInstaller.__main__.run(options)

    return output_dir
