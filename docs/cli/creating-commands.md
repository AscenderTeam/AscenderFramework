# Creating Commands

This guide walks you through creating both BasicCLI and GenericCLI commands in the Ascender Framework.

## Prerequisites

Before creating commands, ensure you have the necessary imports:

```python
from typing import Any
from ascender.core.cli_engine import Command, Handler, BasicCLI, GenericCLI, Parameter
```

## Creating BasicCLI Commands

BasicCLI commands are perfect for single-action operations. Arguments are now defined as class attributes using the `Parameter()` function.

### Step 1: Define the Command Class with Parameters

```python
@Command(name="build", description="Build the application")
class BuildCommand(BasicCLI):
    # Define arguments as class attributes
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
        # Your implementation here
        pass
```

### Step 2: Implement the Execute Method

The `execute` method no longer receives arguments as parameters. Instead, access them via `self`:

```python
@Command(name="build", description="Build the application")
class BuildCommand(BasicCLI):
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
        """Build the application with optional production mode."""
        mode = "production" if self.production else "development"
        print(f"Building in {mode} mode...")
        print(f"Output directory: {self.output}")
        
        # Your build logic here
        if self.production:
            self._optimize_build()
        
        print("Build completed successfully!")
    
    def _optimize_build(self):
        """Private helper method for production optimizations."""
        print("Applying production optimizations...")
```

### Step 3: Handle Arguments

Arguments are defined as class attributes and automatically parsed by the CLI engine:

```python
@Command(name="deploy", description="Deploy the application")
class DeployCommand(BasicCLI):
    environment: str = Parameter(
        "staging",
        description="Target environment",
        names=["--environment", "-e"]
    )
    
    force: bool = Parameter(
        False,
        description="Force deployment without confirmation",
        names=["--force", "-f"]
    )
    
    config_file: str = Parameter(
        None,
        description="Path to configuration file",
        names=["--config", "-c"]
    )
    
    def execute(self) -> None:
        if not self.environment:
            raise ValueError("Environment is required")
        
        print(f"Deploying to {self.environment}")
        
        if self.force:
            print("Force deployment enabled")
        
        if self.config_file:
            print(f"Using config file: {self.config_file}")
```

## Creating GenericCLI Commands

GenericCLI commands organize related functionality into subcommands:

### Step 1: Define the Command Group

```python
@Command(name="database", description="Database management commands")
class DatabaseCommand(GenericCLI):
    pass
```

### Step 2: Add Subcommand Methods with @Handler

Each subcommand method **must** be decorated with `@Handler`:

```python
@Command(name="database", description="Database management commands")
class DatabaseCommand(GenericCLI):
    
    @Handler("migrate", description="Run database migrations")
    def migrate(self, rollback: bool = False, steps: int = None, **kwargs: Any) -> None:
        """Run database migrations."""
        if rollback:
            if steps:
                print(f"Rolling back {steps} migrations")
            else:
                print("Rolling back last migration")
            # Rollback logic here
        else:
            print("Running pending migrations...")
            # Migration logic here
    
    @Handler("seed", description="Seed database with test data")
    def seed(self, clear: bool = False, file: str = None, **kwargs: Any) -> None:
        """Seed database with test data."""
        if clear:
            print("Clearing existing data...")
            # Clear logic here
        
        if file:
            print(f"Seeding from file: {file}")
        else:
            print("Seeding with default data...")
        # Seeding logic here
    
    @Handler("backup", description="Backup database", is_coroutine=True)
    async def backup(self, output: str = "backup.sql", **kwargs: Any) -> None:
        """Async database backup."""
        print(f"Creating backup to {output}...")
        # Async backup logic here
        import asyncio
        await asyncio.sleep(1)  # Simulate async operation
        print("Backup completed!")
```

### Step 3: Add Helper Methods

Use private methods for shared functionality:

```python
@Command(name="database", description="Database management commands")
class DatabaseCommand(GenericCLI):
    
    def migrate(self, **kwargs: Any) -> None:
        """Run database migrations."""
        connection = self._get_connection()
        # Migration logic
    
    def seed(self, **kwargs: Any) -> None:
        """Seed database with test data."""
        connection = self._get_connection()
        # Seeding logic
    
    def _get_connection(self):
        """Private helper method to get database connection."""
        # Database connection logic
        return "database_connection"
    
    def _validate_migration(self, migration_file: str) -> bool:
        """Private helper to validate migration files."""
        # Validation logic
        return True
```

## The @Handler Decorator

### Purpose and Requirements

The `@Handler` decorator is **required** for all GenericCLI subcommands. It serves several critical functions:

1. **Subcommand Registration**: Registers methods as CLI subcommands
2. **Parameter Parsing**: Automatically parses method signatures for arguments
3. **Async Support**: Enables coroutine command handlers
4. **Metadata Storage**: Stores command metadata for help generation

### Basic Handler Usage

```python
from ascender.core.cli_engine import Handler

@Command(name="tools", description="Development tools")
class ToolsCommand(GenericCLI):
    
    @Handler("format", description="Format source code")
    def format_code(self, path: str = ".", **kwargs: Any) -> None:
        """Format code in the specified directory."""
        print(f"Formatting code in {path}")
    
    @Handler("lint", description="Lint source code")  
    def lint_code(self, fix: bool = False, **kwargs: Any) -> None:
        """Run linter on source code."""
        if fix:
            print("Running linter with auto-fix")
        else:
            print("Running linter")
```

### Async Handler Support

For long-running or I/O-bound operations, use async handlers:

```python
@Command(name="network", description="Network operations")
class NetworkCommand(GenericCLI):
    
    @Handler("download", description="Download files", is_coroutine=True)
    async def download_files(self, 
                           url: str,
                           output: str = "./downloads",
                           **kwargs: Any) -> None:
        """Async file download."""
        print(f"Downloading from {url}")
        
        # Simulate async download
        import asyncio
        await asyncio.sleep(2)
        
        print(f"Downloaded to {output}")
    
    @Handler("sync", description="Sync remote data", is_coroutine=True)
    async def sync_data(self, **kwargs: Any) -> None:
        """Async data synchronization."""
        print("Starting data sync...")
        
        # Async operations here
        import asyncio
        await asyncio.sleep(1)
        
        print("Sync completed")
```

### Handler Configuration Options

```python
@Handler(
    "command_name",                    # Subcommand name (required)
    description="Command description", # Help text
    is_coroutine=False,               # Set True for async methods
    **kwargs                          # Additional metadata
)
```

### Multiple Handler Names

You can register multiple names for the same handler:

```python
@Command(name="database", description="Database operations")
class DatabaseCommand(GenericCLI):
    
    @Handler("migrate", "migration", description="Run database migrations")
    def run_migrations(self, **kwargs: Any) -> None:
        """Run database migrations (accessible as both 'migrate' and 'migration')."""
        print("Running migrations...")
```

**Usage**:
```bash
ascender database migrate    # Works
ascender database migration  # Also works
```

The `@Command` decorator supports several options:

### Basic Options

```python
@Command(
    name="custom-name",           # Command name (defaults to class name)
    description="Command help",   # Description for help text
)
class MyCommand(BasicCLI):
    pass
```

### Advanced Options

```python
@Command(
    name="advanced",
    description="Advanced command with custom options",
    aliases=["adv", "a"],         # Command aliases
    hidden=False,                 # Hide from help (useful for debug commands)
    category="Development",       # Group commands by category
)
class AdvancedCommand(BasicCLI):
    pass
```

## Advanced Parameter Configuration

### Using the Parameter() Function

The `Parameter()` function provides fine-grained control over command-line arguments:

```python
from ascender.core.cli_engine import Parameter

@Command(name="deploy", description="Deploy application")
class DeployCommand(BasicCLI):
    def execute(self,
                environment: str = Parameter(
                    description="Target environment",
                    names=["--env", "-e"],
                    action="store"
                ),
                force: bool = Parameter(
                    False,
                    description="Force deployment without confirmation",
                    names=["--force", "-f"]
```

### Parameter Function Options

The `Parameter()` function supports extensive configuration:

```python
Parameter(
    default=None,                    # Default value
    names=["--flag", "-f"],         # CLI flag names
    description="Help text",        # Help description
    action="store",                 # Argument action
    nargs=None,                     # Number of arguments
    const=None,                     # Constant value for store_const
    dest=None,                      # Destination variable name
    metavar="VALUE",                # Help placeholder name
    **kwargs                        # Additional argparse options
)
```

### Advanced Parameter Examples

```python
@Command(name="advanced", description="Advanced parameter examples")
class AdvancedCommand(GenericCLI):
    
    @Handler("process", description="Process files with advanced options")
    def process(self,
                files: list[str] = Parameter(
                    description="Input files to process",
                    names=["--files", "-f"],
                    nargs="+",  # One or more arguments
                    metavar="FILE"
                ),
                output_dir: str = Parameter(
                    default="./output",
                    description="Output directory",
                    names=["--output", "-o"],
                    metavar="DIR"
                ),
                verbose: int = Parameter(
                    default=0,
                    description="Verbosity level (use multiple times: -vvv)",
                    names=["--verbose", "-v"],
                    action="count"
                ),
                format: str = Parameter(
                    default="json",
                    description="Output format",
                    names=["--format"],
                    choices=["json", "xml", "yaml"]
                ),
                **kwargs: Any) -> None:
        
        print(f"Processing {len(files)} files")
        print(f"Output directory: {output_dir}")
        print(f"Verbosity level: {verbose}")
        print(f"Output format: {format}")
```

### Specialized Parameter Types

Use specific parameter functions for common types:

```python
from ascender.core.cli_engine import BooleanParameter, ConstantParameter

@Command(name="special", description="Special parameter types")
class SpecialCommand(BasicCLI):
    def execute(self,
                debug: bool = BooleanParameter(
                    default=False,
                    description="Enable debug mode",
                    flags=["--debug", "-d"]
                ),
                log_level: str = ConstantParameter(
                    const="INFO",
                    default="WARNING",
                    description="Set log level to INFO",
                    flags=["--info"]
                ),
                **kwargs: Any) -> None:
        
        print(f"Debug mode: {debug}")
        print(f"Log level: {log_level}")
```

## Error Handling

Implement proper error handling in your commands:

```python
@Command(name="file-ops", description="File operations")
class FileOpsCommand(GenericCLI):
    
    def copy(self, source: str, destination: str, **kwargs: Any) -> None:
        """Copy a file from source to destination."""
        try:
            import shutil
            shutil.copy2(source, destination)
            print(f"Copied {source} to {destination}")
        except FileNotFoundError:
            print(f"Error: Source file {source} not found")
            return 1  # Exit code for error
        except PermissionError:
            print(f"Error: Permission denied copying to {destination}")
            return 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 1
        
        return 0  # Success exit code
```

## Documentation Best Practices

### Method Docstrings

Use clear docstrings for automatic help generation:

```python
@Command(name="generate", description="Code generation utilities")
class GenerateCommand(GenericCLI):
    
    def controller(self, name: str, **kwargs: Any) -> None:
        """
        Generate a new controller class.
        
        Creates a new controller with basic CRUD operations and proper
        routing configuration. The controller will be placed in the
        controllers directory with appropriate imports.
        
        Args:
            name: The name of the controller (without 'Controller' suffix)
        """
        # Implementation here
        pass
```

### Class Documentation

Document the overall command purpose:

```python
@Command(name="test", description="Testing utilities")
class TestCommand(GenericCLI):
    """
    Testing utilities for the Ascender Framework.
    
    This command group provides various testing-related operations including
    running tests, generating test files, and managing test databases.
    
    Examples:
        ascender test run --coverage
        ascender test generate UserTest
        ascender test database reset
    """
    
    def run(self, coverage: bool = False, **kwargs: Any) -> None:
        """Run the test suite."""
        pass
```

## Next Steps

- Learn about [Command Registration](registration.md) to integrate your commands
- Check out [Examples](examples.md) for real-world command implementations
- Explore the CLI engine source code for advanced customization options
