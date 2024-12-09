import os
from typing import Any
from ascender.common.injectable import Injectable
from ascender.contrib.services import Service
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.schematics.module.edit import ModuleEditor
from ascender.schematics.repository.edit import RepositoryEditor
from ascender.schematics.utilities.case_filters import pascal_case


@Injectable()
class EditGeneratorService(Service):
    def __init__(self):
        ...

    def get_module_path(
        self,
        name: str,
        path: list[str]
    ):
        # print(f"{'/'.join(path)}/{name}_module.py")
        if os.path.exists(f"{'/'.join(path)}/{name}_module.py"):
            return f"{'/'.join(path)}/{name}_module.py"

        if len(path) > 1:
            return self.get_module_path(name, path[:-1])

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
        _path = parent_path.split("/")
        if not (module_path := self.get_module_path(name, _path)):
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