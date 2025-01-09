from typing import Literal, Optional
from pydantic import BaseModel, Field


class LoggingRotationConfig(BaseModel):
    enabled: bool = Field(True, description="Whether log rotation is enabled.")
    max_size: str = Field("10MB", description="Maximum size of a log file before rotation.")
    backup_count: int = Field(5, ge=1, description="Number of backup files to keep.")


class LoggingConfig(BaseModel):
    level: Literal["debug", "info", "warn", "error", "critical"] = Field("info", description="Logging level.")
    file: Optional[str] = Field(None, description="Path to the log file.")
    console: bool = Field(True, description="Whether to enable console logging.")
    rotation: Optional[LoggingRotationConfig] = Field(
        None, description="Log rotation settings."
    )


class BuildConfig(BaseModel):
    target: Literal["development", "production", "test"] = Field(..., description="Build target environment.")
    minify: bool = Field(True, description="Whether to minify the code.")
    obfuscate: bool = Field(True, description="Whether to obfuscate the code.")
    stripComments: bool = Field(True, description="Whether to strip comments from the code.")
    includeStatic: bool = Field(True, description="Whether to include static files in the build.")
    includeLogs: bool = Field(True, description="Whether to include logs in the build.")
    maxBuildSizeMB: int = Field(50, ge=1, description="Maximum allowed build size in MB.")


class ServerConfig(BaseModel):
    workers: int = Field(4, ge=1, description="Number of worker processes.")
    reload: bool = Field(True, description="Whether to enable hot-reload for development.")
    timeout: int = Field(60, ge=1, description="Request timeout in seconds.")
    requestLogging: bool = Field(True, description="Whether to enable detailed request logging.")


class DependencyInjectionConfig(BaseModel):
    strictMode: bool = Field(True, description="Whether to enforce strict mode for dependency injection.")
    circularDependencyHandling: Literal["warn", "error"] = Field(
        "warn", description="Action to take when circular dependencies are detected."
    )


class FeaturesConfig(BaseModel):
    dependencyInjection: DependencyInjectionConfig = Field(..., description="Dependency injection settings.")
    runtimeMonitoring: bool = Field(True, description="Whether to enable runtime monitoring.")
    autoMigrations: bool = Field(False, description="Whether to enable automatic migrations.")
    staticFileServing: bool = Field(True, description="Whether to enable serving of static files.")

