from typing import Annotated
from ascender.clis.tests.tests_cli_service import TestsCLIService
from ascender.core.cli_engine import Command, Parameter, GenericCLI, Handler, BooleanParameter


@Command(name="tests", description="Ascender Framework's testing utilities for unit-testing and integrational testing.")
class TestRunnerCLI(GenericCLI):
    def __init__(self, pytest_interop: TestsCLIService) -> None:
        self.pytest_interop = pytest_interop

    @Handler("init", description="Initialize testing environment in the current project.")
    def init_testing_environment(self, path: Annotated[str, Parameter("tests", names=["-p", "--path"])]) -> None:
        print(f"Initializing testing environment at {path}...")

    @Handler("run", description="Run tests in the current project.")
    def run_tests(
        self, 
        marks: Annotated[list[str] | None, Parameter(default=None, action="extend", names=["-m", "--marks"], nargs="+")],
        verbose: Annotated[bool, BooleanParameter(description="Run tests in verbose mode", flags=["--verbose", "-v"])],
        tb_short: Annotated[bool, BooleanParameter(description="Use short traceback format", flags=["--tb-short"])],
    ) -> None:
        self.pytest_interop.run_tests(verbose=verbose, tb_short=tb_short, marks=marks)