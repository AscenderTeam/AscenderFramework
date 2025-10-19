import os
from pathlib import Path
from typing import Any
from ascender.common.injectable import Injectable
from ascender.core.services import Service
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.schematics.module.edit import ModuleEditor
from ascender.schematics.repository.edit import RepositoryEditor
from ascender.schematics.utilities.case_filters import pascal_case


@Injectable(provided_in="root")
class EditGeneratorService(Service):
    def __init__(self):
        ...

    def get_module_path(
        self,
        name: str,
        path: os.PathLike | str
    ):
        # Use os.path.join for cross-platform compatibility
        module_path = Path(path, f"{name}_module.py").relative_to(os.getcwd())

        if module_path.exists():
            return module_path

        # Recursive check for module in parent directories
        if module_path.parents:
            return self.get_module_path(name, module_path.parent)

        return None

    def update_module(
        self,
        parent_path: str,
        name: str,
        package_imports: dict[str, str],
        imports: list[str],
        providers: list[str],
        declarations: list[str],
    ):
        if not (module_path := self.get_module_path(name, parent_path)):
            return None

        module_editor = ModuleEditor(
            module_path,
            package_imports=package_imports,
            imports=imports,
            providers=providers,
            declarations=declarations
        )
        return module_editor.invoke()

    def update_repository(
            self,
            name: str,
            entities: dict[str, Any],
            orm_mode: ORMEnum,
    ):
        repository_editor = RepositoryEditor(name, entities, orm_mode)

        return repository_editor.invoke()