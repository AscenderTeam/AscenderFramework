from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    github_url: str
    created_at: datetime
    updated_at: datetime

class ProjectDTO(BaseModel):
    name: str
    description: Optional[str]
    getting_started_prompt: Optional[str] = "This is a getting started prompt" # TODO: Make a default getting started prompt
    github_url: str