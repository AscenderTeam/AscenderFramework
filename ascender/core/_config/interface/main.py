from pydantic import BaseModel, Field

from .environment import PathsConfig, EnvironmentsConfig
from .runtime import BuildConfig, LoggingConfig, ServerConfig, FeaturesConfig


class AscenderConfig(BaseModel):
    project: dict[str, str] = Field(..., description="Basic project metadata.")
    paths: PathsConfig = Field(..., description="Paths configuration.")
    logging: LoggingConfig = Field(..., description="Logging configuration.")
    build: BuildConfig = Field(..., description="Build configuration.")
    server: ServerConfig = Field(..., description="Server configuration.")
    features: FeaturesConfig = Field(..., description="Framework features.")
    environment: EnvironmentsConfig = Field(..., description="Environment-specific settings.")