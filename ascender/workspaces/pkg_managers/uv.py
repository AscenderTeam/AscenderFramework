import os
import subprocess
from pathlib import Path

from .base import BasePackageManager


class UVPackageManager(BasePackageManager):
    name = "uv"

    def add(self, source_path: Path, target_dir: Path) -> None:
        # uv writes to [tool.uv.sources] with {path = "...", editable = true}
        # and correctly preserves relative paths when given a relative path.
        rel_path = os.path.relpath(source_path, target_dir)
        subprocess.call(["uv", "add", "--editable", rel_path], cwd=target_dir)
