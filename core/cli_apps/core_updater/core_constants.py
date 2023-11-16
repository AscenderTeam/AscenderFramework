from os import scandir
from core.utils.cacher import AscCacher
from settings import BASE_PATH


class CoreConstants:
    checkup_result: list[dict[str, str | bool]] = []

    def __init__(self) -> None:
        self.core_dir = f"{BASE_PATH}/core"
        self.core_updater_dir = f"{self.core_dir}/cli_apps/core_updater"
        self.core_updater_config = f"{self.core_updater_dir}/config.py"

        self.cacher = AscCacher()

    def core_files(self):
        pass

    def scan_dir_files(self, path: str, child_depth: int = 0) -> list[dict[str, str | bool]]:
        dirs = scandir(path)
        scanned_dirs: list[dict[str, str | bool]] = []

        for directory in dirs:
            if directory.name in ["__pycache__", ".git", ".vscode", ".idea", ".gitignore", ".gitattributes", ".DS_Store"]:
                continue
            if directory.is_dir():
                scanned_dirs.append({
                    "name": directory.name,
                    "is_dir": True,
                    "path": directory.path,
                    "children": self.scan_dir_files(directory.path, child_depth + 1)
                })
                continue
            scanned_dirs.append({
                "name": directory.name,
                "path": directory.path,
                "is_dir": False,
            })

        return scanned_dirs

    def scan_core_files(self, save_last_scan: bool = True):
        dirs = self.scan_dir_files(self.core_dir)
        if save_last_scan:
            self.cacher.save_json_cache(dirs, "core_files")

        return dirs

    def length_of_core_files(self):
        safe_files = self.cacher.load_json_cache("core_files")
        return len(safe_files), len(self.scan_core_files(save_last_scan=False))

    def compare_core_files(self):
        safe_core_files = self.cacher.load_json_cache("core_files")
        current_core_files = self.scan_core_files(save_last_scan=False)

        for safe_core_file in safe_core_files:
            current_core_file = next(
                (item for item in current_core_files if item["name"] == safe_core_file["name"]), None)

            if current_core_file is None:
                self.checkup_result.append({
                    "name": safe_core_file["name"],
                    "is_dir": safe_core_file["is_dir"],
                    "path": safe_core_file["path"],
                    "is_healthy": False
                })
                yield {
                    "name": safe_core_file["name"],
                    "is_dir": safe_core_file["is_dir"],
                    "path": safe_core_file["path"],
                    "is_healthy": False
                }
                continue

            check_path = safe_core_file["path"] == current_core_file["path"]
            check_is_dir = safe_core_file["is_dir"] == current_core_file["is_dir"]
            if safe_core_file["is_dir"]:
                self.checkup_result.append({
                    "name": current_core_file["name"],
                    "is_dir": current_core_file["is_dir"],
                    "path": current_core_file["path"],
                    "children": list(self.compare_files(safe_core_file["children"], current_core_file["children"])),
                    "is_healthy": bool(check_path and check_is_dir)
                })
                yield {
                    "name": current_core_file["name"],
                    "is_dir": current_core_file["is_dir"],
                    "path": current_core_file["path"],
                    "children": list(self.compare_files(safe_core_file["children"], current_core_file["children"])),
                    "is_healthy": bool(check_path and check_is_dir)
                }
            else:
                self.checkup_result.append({
                    "name": current_core_file["name"],
                    "path": current_core_file["path"],
                    "is_dir": current_core_file["is_dir"],
                    "is_healthy": bool(check_path and check_is_dir)
                })
                yield {
                    "name": current_core_file["name"],
                    "path": current_core_file["path"],
                    "is_dir": current_core_file["is_dir"],
                    "is_healthy": bool(check_path and check_is_dir)
                }

    def compare_files(self, safe_files: list[dict[str, str | bool]], current_files: list[dict[str, str | bool]]):

        for safe_core_file in safe_files:
            current_core_file = next(
                (item for item in current_files if item["name"] == safe_core_file["name"]), None)

            if current_core_file is None:
                yield {
                    "name": safe_core_file["name"],
                    "path": safe_core_file["path"],
                    "is_dir": safe_core_file["is_dir"],
                    "is_healthy": False
                }
                continue

            check_is_dir = safe_core_file["is_dir"] == current_core_file["is_dir"]
            check_path = safe_core_file["path"] == current_core_file["path"]

            if current_core_file["is_dir"]:
                yield {
                    "name": current_core_file["name"],
                    "is_dir": current_core_file["is_dir"],
                    "path": current_core_file["path"],
                    "children": list(self.compare_files(safe_core_file["children"], current_core_file["children"])),
                    "is_healthy": bool(check_is_dir and check_path)
                }
            else:
                yield {
                    "name": current_core_file["name"],
                    "path": current_core_file["path"],
                    "is_dir": current_core_file["is_dir"],
                    "is_healthy": bool(check_is_dir and check_path)
                }
