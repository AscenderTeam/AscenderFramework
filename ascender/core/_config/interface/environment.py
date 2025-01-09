from pydantic import BaseModel, Field, conint
from typing import Optional, Literal

from .runtime import BuildConfig


class PathsConfig(BaseModel):
    source: str = Field(..., description="Path to the source directory.")
    root_imports: bool = Field(False, description="Explicitly treat `source` imports as python root imports.")
    output: str = Field(..., description="Path to the build output directory.")
    static: Optional[str] = Field(None, description="Path to the static files directory.")
    logs: Optional[str] = Field(None, description="Path to the logs directory.")
    
class EnvironmentConfig(BaseModel):
    debug: bool = Field(..., description="Whether debugging is enabled.")
    logging: Literal["debug", "info", "warn", "error", "critical"] = Field(..., description="Logging level.")
    build: Optional[BuildConfig] = Field(None, description="Build-specific settings for this environment.")


class EnvironmentsConfig(BaseModel):
    default: Literal["development", "production", "test"] = Field(
        "development", description="The default environment."
    )
    environments: dict[Literal["development", "production", "test"], EnvironmentConfig] = Field(
        ..., description="Environment-specific configurations."
    )
