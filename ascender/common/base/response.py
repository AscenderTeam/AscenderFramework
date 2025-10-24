from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)
