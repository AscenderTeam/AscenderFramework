from typing import TypeAlias

from pydantic import BaseModel


class WorkspaceProject(BaseModel):
    name: str
    path: str


Project: TypeAlias = str | WorkspaceProject

__all__ = [
    "WorkspaceProject",
    "Project",
]
