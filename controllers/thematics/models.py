from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ThematicResponse(BaseModel):
    id: int
    name: str
    issue: str
    filename: str
    project: str
    created_at: datetime
    updated_at: datetime
    
class ThematicDTO(BaseModel):
    name: str
    issue: str
    filename: str
    project_id: int