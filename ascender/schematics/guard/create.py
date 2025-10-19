import os
from typing import Any, Literal
from jinja2 import Environment, Template, FileSystemLoader
from ascender.core._config.asc_config import _AscenderConfig
from ascender.schematics.base.create import SchematicsCreator
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case, snake_case


class GuardCreator(SchematicsCreator):
    def __init__(
        self,
        name: str,
        guard_type: Literal["single", "parametrized"] = "single",
        guards: list[str] | None = None
    ):
        self.path_config = _AscenderConfig().config.paths
        self.name = name
        self.guard_type = guard_type
        self.guards = guards

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(loader=FileSystemLoader(self.base_path))
        self.save_path = f"{self.path_config.source}/{name.lower()}_guard.py"

    def load_template(self):
        self.environment.filters['pascal_case'] = pascal_case
        self.environment.filters['snake_case'] = snake_case
        self.environment.filters['kebab_case'] = kebab_case

        if self.guard_type == "single":
            template = self.environment.get_template(f"/files/guard.py.asctpl")

            return template
        
        template = self.environment.get_template(f"/files/param-guard.py.asctpl")

        return template

    def post_processing(self):
        path = self.name.lstrip("/").split("/")
        name = path[-1]
        
        if self.guard_type == "single":
            return {
                "guard_name": name,
            }
        
        if self.guards is None:
            raise ValueError("Expected list of guards but got None")
        
        return {
            "guard_name": name,
            "guards": self.guards
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
