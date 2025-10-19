import os
import re
from typing import Any, TypeVar, get_type_hints
from jinja2 import Environment, FileSystemLoader, Template
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.schematics.base.edit import SchematicsEditor
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case, snake_case
from ascender.schematics.utilities.entity_filters import entity_field_type, stripped


E = TypeVar("E")


class RepositoryEditor(SchematicsEditor):
    def __init__(
        self,
        name: str,
        entity_imports: dict[str, type[E]],
        orm_mode: ORMEnum
    ):
        self.path_config = _AscenderConfig().config.paths
        self.name = name
        self.entity_imports = entity_imports
        self.orm_mode = orm_mode

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(loader=FileSystemLoader(self.base_path))
        self.work_path = os.path.abspath(os.path.normpath(f"{self.path_config.source}/{name.lower()}_repository.py"))

    def load_file(self):
        with open(self.work_path, "r") as code:
            template = code.read()

        return template

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

    def regex_processing(self, file_contents: str):
        """
        Process the file contents to extract existing imports and providers.
        Add new ones without touching the existing user changes.
        """
        entities = []
        package_imports = {}
        
        for namespace, entity_class in self.entity_imports.items():
            if file_contents.find(namespace) != -1 and file_contents.find(entity_class.__name__) != -1:
                raise ValueError(f"Import of entity {entity_class.__name__} from {namespace} already exists, please remove it to generate repository entities properly!")
            
            package_imports[namespace] = entity_class.__name__
            entities.append({
                "name": entity_class.__name__,
                "fields": get_type_hints(entity_class)
            })
        
        upper_section = file_contents + "\n"

        return upper_section, entities, package_imports.items()

    def post_processing(self, regex_values: dict[str, Any] | list[Any]):
        return {
            **regex_values
        }

    def process_file(self, post_processing: dict[str, Any], template: Template):
        return template.render(**post_processing)

    def save_finalized(self, rendered_template: str):
        # Create the directory or directories if it doesn't exist
        os.makedirs(os.path.dirname(self.work_path), exist_ok=True)

        # Create the controller file containing rendered data
        with open(self.work_path, 'w') as f:
            f.write(rendered_template)

        return {
            "schematic_type": "UPDATE",
            "file_path": os.path.relpath(self.work_path),
            "write_size": os.path.getsize(self.work_path)
        }

    def invoke(self):
        file_contents = self.load_file()
        upper_section, entities, package_imports = self.regex_processing(file_contents)
        post_processing = self.post_processing({
            "upper_section": upper_section,
            "entities": entities,
            "package_imports": package_imports
        })
        template = self.load_template()
        processed_file = self.process_file(post_processing, template)

        return self.save_finalized(processed_file)
