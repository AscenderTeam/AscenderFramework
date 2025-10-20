"""
Example implementations of BasicCLI and GenericCLI commands for the Ascender Framework CLI Engine.

This module demonstrates how to properly structure and implement commands using
the new CLI engine with the @Command decorator.
"""

from typing import Any
from ascender.core.cli_engine import Command, Handler, BasicCLI, GenericCLI, Parameter


@Command(name="version", description="Display the version of Ascender Framework")
class VersionCommand(BasicCLI):
    """
    Example BasicCLI command - single command execution.
    
    Usage: ascender version [--verbose]
    """
    
    verbose: bool = Parameter(
        False,
        description="Show detailed version information",
        names=["--verbose", "-v"]
    )
    
    def execute(self) -> None:
        """Execute the version command."""
        if self.verbose:
            print("Ascender Framework v1.0.0 (detailed info)")
            print("Build: 2024.10.18")
            print("Python version: 3.11+")
        else:
            print("Ascender Framework v1.0.0")


@Command(name="build", description="Build the application")
class BuildCommand(BasicCLI):
    """
    Another BasicCLI example - build command.
    
    Usage: ascender build [--production] [--output <dir>]
    """
    
    production: bool = Parameter(
        False,
        description="Build in production mode",
        names=["--production", "--prod"]
    )
    
    output: str = Parameter(
        "dist",
        description="Output directory",
        names=["--output", "-o"]
    )
    
    def execute(self) -> None:
        """Execute the build command."""
        mode = "production" if self.production else "development"
        print(f"Building application in {mode} mode")
        print(f"Output directory: {self.output}")


@Command(name="generate", description="Generate various project components")
class GenerateCommand(GenericCLI):
    """
    Example GenericCLI command - multi-command group.
    
    Usage: 
        ascender generate controller <name> [--path <path>]
        ascender generate service <name> [--interface]
        ascender generate module <name>
    """
    
    @Handler("controller", description="Generate a new controller")
    def controller(self, name: str, path: str = "src/controllers", **kwargs: Any) -> None:
        """Generate a new controller."""
        print(f"Generating controller '{name}' in {path}")
        
    @Handler("service", description="Generate a new service")
    def service(self, name: str, interface: bool = False, **kwargs: Any) -> None:
        """Generate a new service."""
        if interface:
            print(f"Generating service '{name}' with interface")
        else:
            print(f"Generating service '{name}'")
            
    @Handler("module", description="Generate a new module")
    def module(self, name: str, **kwargs: Any) -> None:
        """Generate a new module."""
        print(f"Generating module '{name}'")


@Command(name="database", description="Database management commands")
class DatabaseCommand(GenericCLI):
    """
    Another GenericCLI example - database management.
    
    Usage:
        ascender database migrate [--rollback]
        ascender database seed [--clear]
        ascender database status
    """
    
    @Handler("migrate", description="Run database migrations")
    def migrate(self, rollback: bool = False, **kwargs: Any) -> None:
        """Run database migrations."""
        if rollback:
            print("Rolling back database migrations")
        else:
            print("Running database migrations")
            
    @Handler("seed", description="Seed the database with test data")
    def seed(self, clear: bool = False, **kwargs: Any) -> None:
        """Seed the database with test data."""
        if clear:
            print("Clearing database before seeding")
        print("Seeding database with test data")
        
    @Handler("status", description="Show database migration status")
    def status(self, **kwargs: Any) -> None:
        """Show database migration status."""
        print("Database migration status:")
        print("✓ 001_create_users_table")
        print("✓ 002_create_posts_table")
        print("✗ 003_add_user_roles (pending)")
