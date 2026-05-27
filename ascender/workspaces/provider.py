from ascender.core import Provider
from ascender.core.cli_engine import useCLI
from ascender.workspaces.projects.manager import WorkspaceProjectManager
from ascender.workspaces.scripts.builtin.projects import WorkspaceCLI


def provideWorkspaces() -> Provider:
    return [WorkspaceProjectManager, useCLI(WorkspaceCLI)]
