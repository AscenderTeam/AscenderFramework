import os
from typing import Any
from jinja2 import Environment, Template, FileSystemLoader
from ascender.core._config.asc_config import _AscenderConfig
from ascender.schematics.base.create import SchematicsCreator
from ascender.schematics.utilities.case_filters import kebab_case, pascal_case, snake_case


class ConfTestCreator(SchematicsCreator):
    def __init__(
        self,
        test_path: str = "tests",
        python_files: str = "test_*",
        python_classes: str = "Test* *Tests",
        python_functions: str = "test_*",
        log_cli: str = "true",
        log_level: str = "INFO",
        asyncio_mode: str = "auto"
    ):
        self.path_config = _AscenderConfig().config.paths
        self.test_path = test_path
        self.python_files = python_files
        self.python_classes = python_classes
        self.python_functions = python_functions
        self.log_cli = log_cli
        self.log_level = log_level
        self.asyncio_mode = asyncio_mode
        
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.environment = Environment(loader=FileSystemLoader(self.base_path))
        self.save_path = os.path.join(self.path_config.source, self.test_path)

    def load_template(self, template_name: str = "tests/conftest.py.asctpl") -> Template:
        self.environment.filters['pascal_case'] = pascal_case
        self.environment.filters['snake_case'] = snake_case
        self.environment.filters['kebab_case'] = kebab_case

        template = self.environment.get_template(f"/files/{template_name}")

        return template

    def post_processing(self):

        return {
            "path": os.path.join(self.path_config.source, self.test_path),
            "python_files": self.python_files,
            "python_classes": self.python_classes,
            "python_functions": self.python_functions,
            "log_cli": self.log_cli,
            "log_level": self.log_level
        }

    def process_template(self, post_processing: dict[str, Any], template: Template):
        return template.render(**post_processing)

    def create_ini(self, rendered_template: str):
        # Create the directory or directories if it doesn't exist
        save_path = os.path.abspath("pytest.ini")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)


        with open(save_path, 'w') as f:
            f.write(rendered_template)
            
        return {
            "schematic_type": "CREATE",
            "file_path": save_path,
            "write_size": os.path.getsize(save_path)
        }
    
    def save_finalized(self, relative_path: str, rendered_template: str):
        save_path = os.path.join(self.save_path, relative_path)
        # Create the directory or directories if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Create the controller file containing rendered data
        with open(save_path, 'w') as f:
            f.write(rendered_template)
            
        return {
            "schematic_type": "CREATE",
            "file_path": save_path,
            "write_size": os.path.getsize(save_path)
        }

    def invoke(self):
        conf_tests = self.load_template("pytest.ini.asctpl")
        
        
        post_processing = self.post_processing()
        processed_template = self.process_template(post_processing, conf_tests)

        results = []

        results.append(self.create_ini(processed_template))

        conftests = self.process_template({}, self.load_template("tests/conftest.py.asctpl"))
        test_initial = self.process_template({}, self.load_template("tests/test_initial.py.asctpl"))

        results.append(self.save_finalized("conftest.py", conftests))
        results.append(self.save_finalized("test_initial.py", test_initial))

        return results
