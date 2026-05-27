from abc import ABC, abstractmethod
from pathlib import Path


class BasePackageManager(ABC):
    name: str

    @abstractmethod
    def add(self, source_path: Path, target_dir: Path) -> None:
        """
        Install source_path as a local path dependency into target_dir.

        Args:
            source_path: Absolute path to the project being installed.
            target_dir:  Absolute path to the project being installed into.
        """
        ...
