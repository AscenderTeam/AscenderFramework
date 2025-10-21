import os
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
    
    
    def create_tests(
        self,
        test_path: str = "tests",
        python_files: str = "test_*",
        python_classes: str = "Test* *Tests",
        python_functions: str = "test_*",
        log_cli: str = "true",
        log_level: str = "INFO",
        asyncio_mode: str = "auto" 
    ) -> bool:
        from ascender.schematics.tests.create import ConfTestCreator

        if os.path.exists(os.path.abspath("pytest.ini")):
            self.console.print(f"[red]⚠️ Error: pytest.ini already exists, failed to initialize tests.[/red]")
            return False
        
        creator = ConfTestCreator(
            test_path=test_path,
            python_files=python_files,
            python_classes=python_classes,
            python_functions=python_functions,
            log_cli=log_cli,
            log_level=log_level,
            asyncio_mode=asyncio_mode
        )
        results = creator.invoke()

        for result in results:
            self.console.print(f"[green]{result['schematic_type']}[/green] {result['file_path']} [cyan]({result['write_size']} bytes)[/cyan]")

        return True