from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ascender.core.di.interface.provider import Provider


def provideCoreCLIs() -> list["Provider"]:
    """
    Single source of truth for the CLI commands that must be registered in BOTH
    the internal launcher (`createInternalApplication`) and the running app
    (`createApplication`) — i.e. the test runners, which are useful from either
    surface and need no running application.

    These previously lived as hand-maintained, duplicated `useCLI(...)` entries in
    each entrypoint, which had already drifted (e.g. the `test` command existed in
    only one of them). Register them here once and compose path-specific commands
    on top: `generate`/run/new/version/workspaces for the launcher; build/serve for
    the app.

    NOTE: `generate` is intentionally NOT here. It used to be registered on the
    running app because repository codegen inspected live ORM models at runtime;
    that path is gone (repositories are deprecated, and codegen is now pure static
    reflection via `import_module` + `get_type_hints`). `generate` is therefore a
    launcher-only command now.
    """
    # Imported lazily to keep these entrypoints free of import-time cycles.
    from ascender.clis.tests.test_app import TestCLI
    from ascender.clis.tests.tests_app import TestRunnerCLI
    from ascender.core.cli_engine import useCLI

    return [
        useCLI(TestRunnerCLI),
        useCLI(TestCLI),
    ]
