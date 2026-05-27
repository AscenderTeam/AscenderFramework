import os
import subprocess
from pathlib import Path
from typing import Optional

import tomlkit

from .base import BasePackageManager


class PoetryPackageManager(BasePackageManager):
    name = "poetry"

    def add(self, source_path: Path, target_dir: Path) -> None:
        pkg_name = self._package_name(source_path)
        if not pkg_name:
            raise Exception(
                f"Could not determine package name from '{source_path / 'pyproject.toml'}'"
            )

        rel_path = os.path.relpath(source_path, target_dir)

        # Write directly to [tool.poetry.dependencies] with a relative path.
        # poetry add writes an absolute file:// URI into [project.dependencies]
        # which is both non-portable and not supported by the PEP 508 file: scheme
        # for relative paths — so we own the write ourselves.
        self._write_dep(target_dir / "pyproject.toml", pkg_name, rel_path)

        subprocess.call(["poetry", "lock"], cwd=target_dir)
        subprocess.call(["poetry", "install"], cwd=target_dir)

    def _package_name(self, source_path: Path) -> Optional[str]:
        toml_path = source_path / "pyproject.toml"
        if not toml_path.exists():
            return None
        try:
            doc = tomlkit.parse(toml_path.read_text(encoding="utf-8"))
            return (
                doc.get("project", {}).get("name")
                or doc.get("tool", {}).get("poetry", {}).get("name")
            )
        except Exception:
            return None

    def _write_dep(self, toml_path: Path, pkg_name: str, rel_path: str) -> None:
        doc = tomlkit.parse(toml_path.read_text(encoding="utf-8"))

        # Navigate / create [tool.poetry.dependencies]
        if "tool" not in doc:
            doc.add("tool", tomlkit.table())
        tool = doc["tool"]  # type: ignore[index]

        if "poetry" not in tool:  # type: ignore[operator]
            tool.add("poetry", tomlkit.table())  # type: ignore[union-attr]
        poetry = tool["poetry"]  # type: ignore[index]

        if "dependencies" not in poetry:  # type: ignore[operator]
            poetry.add("dependencies", tomlkit.table())  # type: ignore[union-attr]
        deps = poetry["dependencies"]  # type: ignore[index]

        entry = tomlkit.inline_table()
        entry.append("path", rel_path)
        entry.append("develop", True)
        deps[pkg_name] = entry  # type: ignore[index, reportIndexIssue]

        toml_path.write_text(tomlkit.dumps(doc), encoding="utf-8")
