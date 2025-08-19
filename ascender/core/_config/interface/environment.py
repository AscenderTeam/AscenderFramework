from pydantic import BaseModel, Field, conint
from typing import Optional, Literal

from .runtime import BuildConfig


class PathsConfig(BaseModel):
    source: str = Field(..., description="Path to the source directory.")
    root_imports: bool = Field(False, description="Explicitly treat `source` imports as python root imports.")
    output: str = Field(..., description="Path to the build output directory.")
    static: Optional[str] = Field(None, description="Path to the static files directory.")
    logs: Optional[str] = Field(None, description="Path to the logs directory.")
    

class OverrideConfig(BaseModel):
    enabled: bool = Field(True, description="Whether dependency injection overrides are enabled.")
    injector: Optional[str] = Field(
        None, description="Custom injector class to use for dependency injection overrides."
    )


class EnvironmentConfig(BaseModel):
    debug: bool = Field(..., description="Whether debugging is enabled.")
    logging: Literal["debug", "info", "warn", "error", "critical"] = Field(..., description="Logging level.")
    build: Optional[BuildConfig] = Field(None, description="Build-specific settings for this environment.")
    overrides: OverrideConfig = Field(
        OverrideConfig(enabled=False, injector="ascender.core.di.injector.AscenderInjector"), 
        description="Dependency injection settings for this environment."
    )


class EnvironmentsConfig(BaseModel):
    default: Literal["development", "production", "test"] = Field(
        "development", description="The default environment."
    )
    environments: dict[Literal["development", "production", "test"], EnvironmentConfig] = Field(
        ..., description="Environment-specific configurations."
    )
