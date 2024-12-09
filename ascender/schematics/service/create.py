import os
from typing import Any
from jinja2 import Environment, FileSystemLoader, Template
from ascender.schematics.base.create import SchematicsCreator
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case, snake_case


class ServiceCreator(SchematicsCreator):
    def __init__(
        self,
        name: str
    ):
        self.name = name

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(loader=FileSystemLoader(self.base_path))
        self.save_path = f"{name.lower()}_service.py"

    def load_template(self):
        self.environment.filters['pascal_case'] = pascal_case
        self.environment.filters['snake_case'] = snake_case
        self.environment.filters['kebab_case'] = kebab_case

        template = self.environment.get_template("files/service.py.asctpl")

        return template

    def post_processing(self):
        path = self.name.lstrip("/").split("/")
        name = path[-1]

        return {
            "service_name": name
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
