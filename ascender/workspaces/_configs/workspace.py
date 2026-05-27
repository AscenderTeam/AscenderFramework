from pydantic import BaseModel, Field

from .workspace_project import Project
from .workspace_script import WorkspaceScript


class WorkspaceConfigs(BaseModel):
    version: str = "1.0"
    name: str
    projects: list[Project]
    scripts: list[WorkspaceScript] = Field(default_factory=list)
