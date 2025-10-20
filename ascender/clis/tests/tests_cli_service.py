from ascender.common.injectable import Injectable
from ascender.core._config.asc_config import _AscenderConfig

from rich.console import Console


@Injectable(provided_in="root")
class TestsCLIService:
    def __init__(self) -> None:
        self.console = Console()

    def run_tests(self, verbose: bool, tb_short: bool, marks: list[str] | None = None, path: str | None = None) -> None:
        import pytest
        _AscenderConfig.is_test = True
        configs = _AscenderConfig()

        configs.is_test = True
        
        base_path = configs.config.paths.source

        pytest_args = []

        if verbose:
            pytest_args.append("-v")
        
        if tb_short:
            pytest_args.append("--tb=short")
        
        if marks:
            for mark in marks:
                pytest_args.extend(["-m", mark])

        if path:
            pytest_args.append(path if base_path in path else f"{base_path}/{path}")

        self.console.print("[bold blue]🧪 Running Ascender Tests...[/bold blue]")

        pytest.main(pytest_args)
    