from ascender.clis.tests.tests_cli_service import TestsCLIService
from ascender.core.cli_engine import Command, BasicCLI, Parameter, BooleanParameter


@Command(
    name="test",
    description="Run the project's test suite (pytest, inside the Ascender venv).",
    help="Run tests directly: `ascender test`, `ascender test -m unit`, `ascender test --verbose`.",
)
class TestCLI(BasicCLI):
    """
    Singular, ergonomic entrypoint for running the test suite.

    Equivalent to the `tests run` handler but reachable as a single word, so the
    common case reads `ascender test` instead of the doubled `tests run`. The
    `tests` command (with `init` / `run`) remains for scaffolding and back-compat.
    """

    marks: list[str] = Parameter(
        default_factory=list,
        names=["-m", "--marks"],
        action="extend",
        nargs="+",
        description="Only run tests matching the given pytest mark expression(s).",
    )
    verbose: bool = BooleanParameter(
        description="Run tests in verbose mode.", flags=["--verbose", "-v"]
    )
    tb_short: bool = BooleanParameter(
        description="Use short traceback format.", flags=["--tb-short"]
    )

    def __init__(self, pytest_interop: TestsCLIService) -> None:
        self.pytest_interop = pytest_interop

    def execute(self):
        self.pytest_interop.run_tests(
            verbose=self.verbose,
            tb_short=self.tb_short,
            marks=self.marks or None,
        )
