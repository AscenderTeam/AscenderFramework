import os
from pathlib import Path
from typing import Literal

import chardet

from core.cli_apps.controllers_manager.types.structure_metadata import StructureMetadata
from settings import BASE_PATH


class TLoader:
    def __init__(self, template_type: Literal["basic", "auth"],
                 **template_placeholders) -> None:
        self.template_type = template_type
        self.template_placeholders = template_placeholders
        self.metadatas = []
        self.structure_memory = []
    
    def define_metadata(self, metadata: list[StructureMetadata]):
        self.metadatas.append(metadata)
    
    def load_fromdir(self, dirpath: os.PathLike, fill_template: bool = True):
        structures = os.listdir(dirpath)

        for item in structures:
            if item in ["__pycache__"]:
                continue
            print(item, os.path.isdir(item))
            if os.path.isdir(f"{dirpath}/{item}"):
                yield {
                    "type": "dir",
                    "dirname": item,
                    "items": list(self.load_fromdir(f"{dirpath}/{item}"))
                }
                continue

            if item.find(".txt") == -1:
                print(item, "doesn't contain .txt, skipping")
                continue
            
            content = ""
            with open(f"{dirpath}/{item}", "rb") as tpl:
                tpl.seek(0)
                content = tpl.read()
                encoding = chardet.detect(content)["encoding"]
                content = content.decode(encoding)

            if not fill_template:
                yield {
                    "type": "file",
                    "filename": item.replace(".txt", ".py"),
                    "template": content
                }
                continue
            
            for name, value in self.template_placeholders.items():
                content = content.replace(f"[{name}]", value)
            
            yield {
                "type": "file",
                "filename": item.replace(".txt", ".py"),
                "template": content
            }

    def load_structure(self, fill_template: bool = True):
        _path = f"{BASE_PATH}/core/cli_apps/controllers_manager/templates/{self.template_type}"
        
        for item in self.load_fromdir(_path):
            self.structure_memory.append(item)
    
    def develop_dir(self, _to: os.PathLike, structures: dict[str, str]):
        path = Path(_to)
        if not path.exists():
            path.mkdir()
        
        for structure in structures:
            if structure["type"] == "dir":
                self.develop_dir(f"{_to}/{structure['dirname']}", structure["items"])
                continue

            with open(f"{_to}/{structure['filename']}", "w") as f:
                f.write(structure["template"])
        
        return True
        
    def load_template(self, _to: os.PathLike):
        path = Path(_to)
        
        if not path.exists():
            path.mkdir()

        if path.is_file():
            return False
        
        return self.develop_dir(_to, self.structure_memory)