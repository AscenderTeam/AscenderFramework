# Command Types

The Ascender CLI engine provides two distinct command types to handle different use cases. Understanding when to use each type is crucial for building an effective command-line interface.

## BasicCLI Commands

BasicCLI commands are designed for **single-action operations**. They implement one `execute()` method that handles all the command's functionality.

### When to Use BasicCLI

- **Simple Operations**: Version display, status checks, configuration dumps
- **Build Tasks**: Compilation, bundling, deployment
- **Initialization**: Project setup, scaffolding
- **Standalone Actions**: Any command that performs one specific task

### Structure

```python
from ascender.core.cli_engine import Command, BasicCLI, Parameter

@Command(name="command_name", description="Command description")
class MyCommand(BasicCLI):
    # Define arguments as class attributes
    arg_name: type = Parameter(
        default_value,
        description="Argument description",
        names=["--arg-name", "-a"]
    )
    
    def execute(self) -> None:
        # Access arguments via self.arg_name
        pass
```

### Command Pattern

```bash
ascender <command_name> [options]
```

### Example

```python
@Command(name="version", description="Display framework version")
class VersionCommand(BasicCLI):
    verbose: bool = Parameter(
        False,
        description="Show detailed version information",
        names=["--verbose", "-v"]
    )
    
    def execute(self) -> None:
        if self.verbose:
            print("Ascender Framework v1.0.0")
            print("Build: 2024.10.18")
            print("Python: 3.11+")
        else:
            print("Ascender Framework v1.0.0")
```

**Usage**:
```bash
ascender version
ascender version --verbose
```

## GenericCLI Commands

GenericCLI commands are designed for **multi-command groups**. They contain multiple methods, each representing a different subcommand within the same functional area.

### When to Use GenericCLI

- **Related Operations**: Code generation, database management, testing
- **CRUD Operations**: Create, read, update, delete workflows
- **Multi-Step Processes**: Commands that have multiple related actions
- **Grouped Functionality**: When you have several commands that logically belong together

### Structure

```python
from ascender.core.cli_engine import Command, Handler, GenericCLI
from typing import Any

@Command(name="group_name", description="Group description")
class MyCommandGroup(GenericCLI):
    
    @Handler("subcommand1", description="First subcommand")
    def subcommand1(self, **kwargs: Any) -> None:
        # First subcommand implementation
        pass
    
    @Handler("subcommand2", description="Second subcommand", is_coroutine=True)
    async def subcommand2(self, **kwargs: Any) -> None:
        # Async subcommand implementation
        pass
```

### The @Handler Decorator

GenericCLI subcommands **must** be decorated with the `@Handler` decorator to register them properly with the CLI engine. The Handler decorator:

- **Registers subcommands**: Makes methods available as CLI subcommands
- **Supports coroutines**: Can handle both sync and async methods with `is_coroutine=True`
- **Parameter parsing**: Automatically parses method signatures for CLI arguments
- **Metadata extraction**: Stores command metadata for help generation

```python
@Handler(
    "command_name",                    # Subcommand name
    description="Command description", # Help text
    is_coroutine=False,               # Set to True for async methods
    **kwargs                          # Additional options
)
```

### Command Pattern

```bash
ascender <group_name> <subcommand> [options]
```

### Example

```python
@Command(name="generate", description="Generate project components")
class GenerateCommand(GenericCLI):
    
    @Handler("controller", description="Generate a new controller")
    def controller(self, name: str, path: str = "src/controllers", **kwargs: Any) -> None:
        """Generate a new controller."""
        print(f"Creating controller {name} in {path}")
        # Controller generation logic here
    
    @Handler("service", description="Generate a new service")
    def service(self, name: str, interface: bool = False, **kwargs: Any) -> None:
        """Generate a new service."""
        print(f"Creating service {name}")
        if interface:
            print("Including interface definition")
        # Service generation logic here
    
    @Handler("migrate", description="Run database migrations", is_coroutine=True)
    async def migrate(self, rollback: bool = False, **kwargs: Any) -> None:
        """Async database migration handler."""
        if rollback:
            print("Rolling back migrations...")
        else:
            print("Running migrations...")
        # Async migration logic here
```**Usage**:
```bash
ascender generate controller UserController
ascender generate controller UserController --path src/api/controllers
ascender generate service UserService --interface
ascender generate model User --database main
```

## Key Differences

| Aspect | BasicCLI | GenericCLI |
|--------|----------|------------|
| **Purpose** | Single action | Group of related actions |
| **Methods** | One `execute()` method | Multiple command methods |
| **CLI Pattern** | `ascender <cmd> [args]` | `ascender <group> <subcmd> [args]` |
| **Use Cases** | Version, build, init | Generate, database, test |
| **Complexity** | Simple, focused | Organized, multi-functional |
| **Arguments** | Direct to execute | Per-method arguments |

## Choosing the Right Type

### Use BasicCLI when:
- ✅ Your command does one specific thing
- ✅ You don't anticipate adding related subcommands
- ✅ The functionality is simple and focused
- ✅ You want a direct command-to-action mapping

### Use GenericCLI when:
- ✅ You have multiple related commands
- ✅ Commands share a common theme or domain
- ✅ You want to organize commands into logical groups
- ✅ You anticipate adding more related commands in the future

## Method Discovery (GenericCLI)

For GenericCLI commands, the CLI engine discovers subcommands through the `@Handler` decorator:

1. **Handler Registration**: Only methods decorated with `@Handler` become subcommands
2. **Metadata Parsing**: Handler extracts parameter information from method signatures
3. **Coroutine Support**: Async methods are supported when `is_coroutine=True` is specified
4. **Help Generation**: Handler descriptions and method docstrings generate help text
5. **Parameter Validation**: Automatic type checking and argument validation

!!! tip "Handler Decorator Required"
    Unlike basic method discovery, GenericCLI subcommands **must** use the `@Handler` decorator. This ensures proper registration and metadata extraction.

!!! info "Async Support"
    The CLI engine fully supports async subcommands. Simply set `is_coroutine=True` in the Handler decorator and define your method as `async def`.

!!! warning "Method Visibility"
    Only methods with the `@Handler` decorator are registered as subcommands. Public methods without this decorator will be ignored by the CLI engine.
