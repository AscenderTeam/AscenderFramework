from datetime import datetime
import json
import os
import shutil


def build_file_manager(
    project_name: str, 
    output_dir: str, 
    version: str, 
    source_dir: str | None = None, 
    static_dir: str | None = None
):
    """
    Build File Manager for building all source and required files to run built Ascender Framework.
    Specifically generates `build_metadata.json` and copy of `ascender.json`

    Args:
        output_dir (str): Build directory to output all built data
        source (str | None, optional): If specified, it just copies all files in source dir (by default in json is `src/`) to `output_dir`. Defaults to None.
    """
    # Absolute paths
    output_dir = os.path.abspath(f"{output_dir}/{project_name}")
    source_dir = os.path.abspath(source_dir) if source_dir else None
    static_dir = os.path.abspath(static_dir) if static_dir else None

    configuration_json = os.path.abspath("ascender.json")

    # Check in case if there is no directory for output_dir
    os.makedirs(output_dir, exist_ok=True)

    shutil.copy(configuration_json, f"{output_dir}/ascender.json")

    build_metadata = {
        "is_build": True,
        "build_time": datetime.now().isoformat(),
        "build_version": version
    }

    with open(f"{output_dir}/build_metadata.json", "w") as f:
        f.write(json.dumps(build_metadata))
    
    if source_dir:
        shutil.copytree(source_dir, output_dir, dirs_exist_ok=True)
    
    if static_dir:
        shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
    
    return output_dir