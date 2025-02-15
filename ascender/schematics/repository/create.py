import os
from typing import Any, TypeVar, get_type_hints
from jinja2 import Environment, FileSystemLoader, Template
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.schematics.base.create import SchematicsCreator
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case, snake_case
from ascender.schematics.utilities.entity_filters import entity_field_type, stripped


E = TypeVar("E")


class RepositoryCreator(SchematicsCreator):
    def __init__(
        self,
        name: str,
        entity_imports: dict[str, type[E]],
        orm_mode: ORMEnum,
        is_root: bool = True
    ):
        self.path_config = _AscenderConfig().config.paths
        self.name = name
        self.entity_imports = entity_imports
        self.orm_mode = orm_mode
        self.is_root = is_root

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(loader=FileSystemLoader(self.base_path))
        self.save_path = f"{self.path_config.source}/{name.lower()}_repository.py"

    def load_template(self):
        self.environment.filters['pascal_case'] = pascal_case
        self.environment.filters['snake_case'] = snake_case
        self.environment.filters['kebab_case'] = kebab_case
        self.environment.filters['stripped'] = stripped
        self.environment.filters['field_type'] = entity_field_type
        
        if self.orm_mode == ORMEnum.TORTOISE:
            template = self.environment.get_template("/files/to-repository-record.py.asctpl")

            return template
        
        template = self.environment.get_template("/files/sa-repository-record.py.asctpl")
        
        return template

    def post_processing(self):
        path = self.name.lstrip("/").split("/")
        name = path[-1]

        upper_section = self.environment.get_template("/files/repository.py.asctpl")
        upper_section = upper_section.render(repository_name=name)
        
        entities = []
        package_imports = {}

        for namespace, entity_class in self.entity_imports.items():
            package_imports[namespace] = entity_class.__name__
            entities.append({
                "name": entity_class.__name__,
                "fields": get_type_hints(entity_class)
            })

        return {
            "repository_name": name,
            "upper_section": upper_section,
            "package_imports": package_imports.items(),
            "is_root": self.is_root,
            "entities": entities,
        }

    def process_template(self, post_processing: dict[str, Any], template: Template):
        return template.render(**post_processing)

    def save_finalized(self, rendered_template: str):
        # Create the directory or directories if it doesn't exist
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

        # Create the controller file containing rendered data
        _project_root = os.getcwd()
        with open(f"{_project_root}/{self.save_path}", 'w') as f:
            f.write(rendered_template)
            
        return {
            "schematic_type": "CREATE",
            "file_path": self.save_path,
            "write_size": os.path.getsize(f"{_project_root}/{self.save_path}")
        }

    def invoke(self):
        template = self.load_template()
        post_processing = self.post_processing()
        processed_template = self.process_template(post_processing, template)

        return self.save_finalized(processed_template)
