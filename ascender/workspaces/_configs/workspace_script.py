from pydantic import BaseModel


class WorkspaceScript(BaseModel):
    name: str
    command: str | list[str]
    cwd: str | None = None
