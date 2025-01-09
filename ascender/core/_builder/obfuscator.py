import os
import PyInstaller.__main__


def obfuscate_project(project_name: str, output_dir: str, source_dir: str):
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
    source_dir = os.path.abspath(f"{source_dir}/main.py")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define PyArmor obfuscation options
    options = [
        source_dir,    # Source directory
        "--onefile",   # Batch everything into one file
        "--noconfirm",
        "--recursive-copy-metadata", "tortoise-orm",
        "--recursive-copy-metadata", "readchar",
        "--hidden-import=pydantic_core",
        "--hidden-import=pydantic.typing",
        "--hidden-import=pydantic",
        "--hidden-import=uvicorn",
        "--add-data", "ascender.json:ascender.json",
        "--distpath", output_dir
    ]

    # Run PyArmor obfuscation
    PyInstaller.__main__.run(options)

    return output_dir