import os
import sys
from ascender.core._config.asc_config import _AscenderConfig


def configure_imports():
    configs = _AscenderConfig().config

    source_path = os.path.abspath(configs.paths.source)
    root_imports = configs.paths.root_imports

    if root_imports and source_path not in sys.path:
        sys.path.insert(0, source_path)