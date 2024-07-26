from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)