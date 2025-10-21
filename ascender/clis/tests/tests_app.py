from os import name
import os
from typing import Annotated
from ascender.clis.tests.tests_cli_service import TestsCLIService
from ascender.core.cli_engine import Command, Parameter, GenericCLI, Handler, BooleanParameter


@Command(name="tests", description="Ascender Framework's testing utilities for unit-testing and integrational testing.")
class TestRunnerCLI(GenericCLI):
    def __init__(self, pytest_interop: TestsCLIService) -> None:
        self.pytest_interop = pytest_interop

    @Handler("init", description="Initialize testing environment in the current project.")
    def init_testing_environment(
        self, 
        path: Annotated[str, Parameter("tests", names=["-p", "--path"])],
        python_files: Annotated[str, Parameter("test_*", names=["--python-files"])],
        python_classes: Annotated[str, Parameter("Test* *Tests", names=["--python-classes"])],
        python_functions: Annotated[str, Parameter("test_*", names=["--python-functions"])],
        log_cli: Annotated[str, Parameter("true", names=["--log-cli"])],
        log_level: Annotated[str, Parameter("INFO", names=["--log-level"])],
        asyncio_mode: Annotated[str, Parameter("auto", names=["--asyncio-mode"])],
    ) -> None:
        print(f"Initializing testing environment at {path}...")
        _created = self.pytest_interop.create_tests(
            test_path=path,
            python_files=python_files,
            python_classes=python_classes,
            python_functions=python_functions,
            log_cli=log_cli,
            log_level=log_level,
            asyncio_mode=asyncio_mode
        )
        
        if not _created:
            return
        
        self.pytest_interop.console.print("[bold green]✅ Testing environment initialized successfully![/bold green]")
        self.pytest_interop.console.print("[cyan]🛠️ To customize testing configuration, please edit pytest.ini in root of your project. [/cyan]")
        self.pytest_interop.console.print(f"[bold blue] 🧪 Your pytest fixtures and conftests are located at {os.path.abspath(path)}. [/bold blue]")
        self.pytest_interop.console.print("[yellow]💡 Tip: You can run tests using 'ascender tests run' command. [/yellow]")

    @Handler("run", description="Run tests in the current project.")
    def run_tests(
        self, 
        marks: Annotated[list[str] | None, Parameter(default=None, action="extend", names=["-m", "--marks"], nargs="+")],
        verbose: Annotated[bool, BooleanParameter(description="Run tests in verbose mode", flags=["--verbose", "-v"])],
        tb_short: Annotated[bool, BooleanParameter(description="Use short traceback format", flags=["--tb-short"])],
    ) -> None:
        self.pytest_interop.run_tests(verbose=verbose, tb_short=tb_short, marks=marks)