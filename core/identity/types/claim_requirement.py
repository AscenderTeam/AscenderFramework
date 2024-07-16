from pydantic import BaseModel


AppropriateValues = str | int | bool | float

class ClaimRequirement(BaseModel):
    claim: str
    value: AppropriateValues | list[AppropriateValues]
    error_code: int = 403