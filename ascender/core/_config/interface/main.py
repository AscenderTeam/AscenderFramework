from pydantic import BaseModel, Field

from .environment import EnvironmentsConfig, PathsConfig
from .runtime import BuildConfig, FeaturesConfig, LoggingConfig, ServerConfig


class AscenderConfig(BaseModel):
    project: dict[str, str] = Field(..., description="Basic project metadata.")
    paths: PathsConfig = Field(..., description="Paths configuration.")
    logging: LoggingConfig = Field(..., description="Logging configuration.")
    build: BuildConfig = Field(..., description="Build configuration.")
    server: ServerConfig = Field(..., description="Server configuration.")
    features: FeaturesConfig = Field(..., description="Framework features.")
    environment: EnvironmentsConfig = Field(
        ..., description="Environment-specific settings."
    )
