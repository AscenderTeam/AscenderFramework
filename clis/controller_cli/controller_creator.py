from pathlib import Path
from typing import Generator
from clis.controller_cli.constants import ControllerConstants

class ControllerCreator:
    def __init__(self, controller_name: str, controller_path: str = "controllers") -> None:
        self.controller_constants = ControllerConstants(controller_name, controller_path)

    def create_controller(self) -> Generator[str, None, None]:
        path_manager = Path(self.controller_constants.controllers_path, self.controller_constants.controller_name.lower())

        if not path_manager.exists():
            path_manager.mkdir()

        # Handle files
        mandatory_files = self.controller_constants.get_mandatory_files()
        
        for mandatory_file in mandatory_files:
            self.create_file(mandatory_file["path"], mandatory_file["content"])
            yield mandatory_file['name']
    
    def create_optional_files(self) -> Generator[str, None, None]:
        path_manager = Path(self.controller_constants.controllers_path, self.controller_constants.controller_name.lower())

        if not path_manager.exists():
            path_manager.mkdir()

        # Handle files
        optional_files = self.controller_constants.get_optional_files()
        
        for optional_file in optional_files:
            self.create_file(optional_file["path"], optional_file["content"])
            yield optional_file['name']
    
    def create_file(self, fpath: str, contents: str):
        with open(fpath, "w") as f:
            f.write(contents)