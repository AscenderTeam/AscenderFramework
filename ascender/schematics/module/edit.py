import os
import re
from typing import Any
from jinja2 import Environment, FileSystemLoader, Template
from ascender.schematics.base.edit import SchematicsEditor
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case, snake_case


class ModuleEditor(SchematicsEditor):
    def __init__(
        self,
        path: str,
        package_imports: dict[str, str],
        imports: list[str],
        providers: list[str],
        declarations: list[str]
    ):
        self.imports = imports
        self.providers = providers
        self.declarations = declarations
        self.package_imports = package_imports

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(loader=FileSystemLoader(self.base_path))
        self.work_path = path

    def load_file(self):
        with open(self.work_path, "r") as code:
            template = code.read()

        return template

    def load_template(self):
        self.environment.filters['pascal_case'] = pascal_case
        self.environment.filters['snake_case'] = snake_case
        self.environment.filters['kebab_case'] = kebab_case

        template = self.environment.get_template("/files/update-module.py.asctpl")

        return template

    def regex_processing(self, file_contents: str):
        """
        Process the file contents to extract existing imports and providers.
        Add new ones without touching the existing user changes.
        """
        # Regular expressions to detect `imports` and `providers` blocks
        imports_regex = r"imports\s*=\s*\[(.*?)\],"
        providers_regex = r"providers\s*=\s*\[(.*?)\],"

        # Find positions of imports and providers
        imports_match = re.search(imports_regex, file_contents, re.DOTALL)
        providers_match = re.search(providers_regex, file_contents, re.DOTALL)

        if not imports_match or not providers_match:
            raise ValueError("imports or providers block not found")

        # Extract the sections
        upper_section = file_contents[:imports_match.start()]
        lower_section = file_contents[providers_match.end():]

        # Extract current imports and providers
        existing_imports = re.findall(
            r"imports\s*=\s*\[(.*?)\]", file_contents, re.DOTALL)
        existing_providers = re.findall(
            r"providers\s*=\s*\[(.*?)\]", file_contents, re.DOTALL)
        
        existing_declarations = re.findall(
            r"declarations\s*=\s*\[(.*?)\]", file_contents, re.DOTALL)

        if "AscModule" in existing_imports:
            existing_imports.remove("AscModule")
        
        # Remove duplicates by converting to sets and back to list
        final_imports = list(set(self.imports + [imp.strip(
        ) for imp in existing_imports[0].split(",") if imp.strip()]))
        final_providers = list(set(self.providers + [provider.strip(
        ) for provider in existing_providers[0].split(",") if provider.strip()]))
        final_declarations = list(set(self.declarations + [declaration.strip(
        ) for declaration in existing_declarations[0].split(",") if declaration.strip()]))

        removable_packages = []
        # Handle package imports
        for namespace, package in self.package_imports.items():
            if file_contents.find(namespace) != -1 and file_contents.find(package) != -1:
                removable_packages.append(namespace)

        for namespace in removable_packages:
            del self.package_imports[namespace]

        return upper_section, final_imports, final_declarations, final_providers, lower_section

    def post_processing(self, regex_values: dict[str, Any] | list[Any]):
        return {
            "package_imports": self.package_imports.items(),
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
        upper_section, final_imports, final_declarations, final_providers, lower_section = self.regex_processing(file_contents)
        post_processing = self.post_processing({
            "upper_section": upper_section,
            "final_imports": final_imports, 
            "final_declarations": final_declarations,
            "final_providers": final_providers, 
            "lower_section": lower_section
        })
        template = self.load_template()
        processed_file = self.process_file(post_processing, template)

        return self.save_finalized(processed_file)
