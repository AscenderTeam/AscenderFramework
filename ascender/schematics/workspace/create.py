import os
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template

from ascender.schematics.base.create import SchematicsCreator


class WorkspaceCreator(SchematicsCreator):
    def __init__(self, name: str, path: str | None = None):
        """
        Args:
            name: Workspace name, stored in workspace.json and used as the
                  directory name when path is not provided.
            path: Directory to create the workspace in. Defaults to a new
                  subdirectory named after the workspace in the current directory.
        """
        self.name = name
        self.path = path or os.path.join(os.getcwd(), name)

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(
            loader=FileSystemLoader(f"{self.base_path}/files")
        )

        self.templates = {
            "workspace": "workspace.json.asctpl",
            "main": "main.py.asctpl",
        }

        self.save_paths = {
            "workspace": "workspace.json",
            "main": "main.py",
        }

    def load_template(self, template: str) -> Template | None:
        if not (template_file := self.templates.get(template)):
            return None

        return self.environment.get_template(template_file)

    def post_processing(self, template: str) -> dict[str, Any]:
        if template == "workspace":
            return {"workspace_name": self.name}

        return {}

    def process_template(self, post_processing: dict[str, Any], template: Template) -> str:
        return template.render(**post_processing)

    def save_finalized(self, template_name: str, rendered_template: str) -> dict[str, Any]:
        save_path = os.path.normpath(
            os.path.join(self.path, self.save_paths[template_name])
        )

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w") as f:
            f.write(rendered_template)

        return {
            "schematic_type": "CREATE",
            "file_path": os.path.relpath(save_path),
            "write_size": os.path.getsize(save_path),
        }

    def invoke(self) -> list[dict[str, Any]]:
        os.makedirs(self.path, exist_ok=True)

        saved: list[dict[str, Any]] = []

        for template_name in self.templates:
            template = self.load_template(template_name)
            if not template:
                continue

            post_processing = self.post_processing(template_name)
            rendered = self.process_template(post_processing, template)
            saved.append(self.save_finalized(template_name, rendered))

        return saved
