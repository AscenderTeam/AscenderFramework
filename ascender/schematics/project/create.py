import os

from jinja2 import Environment, FileSystemLoader
from ascender.core.database.types.orm_enum import ORMEnum
from ascender.schematics.base.create import SchematicsCreator
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case, snake_case


class ProjectCreator(SchematicsCreator):
    def __init__(
        self,
        path: str,
        orm_mode: ORMEnum,
        standalone: bool
    ):
        self.path = path
        self.orm_mode = orm_mode
        self.standalone = standalone

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(loader=FileSystemLoader(f"{self.base_path}/files"))
        self.save_paths = {
            "main": "src/main.py",
            "bootstrap": "src/bootstrap.py",
            "app_module": "src/app_module.py",
            "gitignore": ".gitignore",
            "settings": "src/settings.py",
            "routes": "src/routes.py",
            "configs": "ascender.json",
            "license": "LICENSE",
            "readme": "README.md",
            "requirements": "requirements.txt"
        }

        self.templates = {
            "main": "main.py.asctpl",
            "bootstrap": "bootstrap.py.asctpl",
            "app_module": "app_module.py.asctpl",
            "routes": "routes.py.asctpl",
            "gitignore": ".gitignore",
            "configs": "ascender.json.asctpl",
            "settings": "settings.py.asctpl",
            "readme": "README.md"
        }

    def load_template(self, template: str):
        self.environment.filters['pascal_case'] = pascal_case
        self.environment.filters['snake_case'] = snake_case
        self.environment.filters['kebab_case'] = kebab_case

        if not (template := self.templates.get(template, None)):
            return None

        return self.environment.get_template(template)

    def post_processing(self, template: str):
        if template == "settings":
            return {
                "connection_type": f"{self.orm_mode.value}.asctpl"
            }

        return {"projectname": os.path.normpath(self.path).replace("\\", "/").split("/")[-1], "standalone": self.standalone, "orm_mode": self.orm_mode.name}

    def process_template(self, post_processing, template):
        return template.render(**post_processing)

    def save_finalized(self, template_name: str, rendered_template: str):
        # Get save path of template
        save_path = f"{self.path}/{self.save_paths[template_name]}"

        # Create the directory or directories if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Create the controller file containing rendered data
        with open(os.path.normpath(save_path), 'w') as f:
            f.write(rendered_template)

        return {
            "schematic_type": "CREATE",
            "file_path": os.path.relpath(os.path.normpath(save_path)),
            "write_size": os.path.getsize(os.path.normpath(save_path))
        }

    def invoke(self):
        # Defining empty rendered templates
        rendered_templates: dict[str, str] = {}

        # Rendering templates & saving them into rendered templates
        for template_name, _ in self.templates.items():
            if template_name == "bootstrap" and self.standalone:
                continue
            
            if template_name == "app_module" and not self.standalone:
                continue

            if not (template := self.load_template(template_name)):
                return None

            post_processing = self.post_processing(template_name)
            rendered_templates[template_name] = self.process_template(
                post_processing, template)

        # Defining SAVED templates
        saved_templates: list[dict[str, str]] = []

        # Handle templates by creating directories, files and filling them up with rendered template content
        for template_name, rendered_template in rendered_templates.items():
            saved_templates.append(self.save_finalized(template_name, rendered_template))

        return saved_templates