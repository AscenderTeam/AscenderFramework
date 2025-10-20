# CLI Overview

The Ascender Framework provides a powerful and flexible Command Line Interface (CLI) system that allows you to create custom commands for your application. The CLI system supports two distinct command patterns to handle different use cases and integrates seamlessly with the framework's dependency injection system.

## Features

- **Type-Safe Commands**: Automatic type detection and validation
- **Decorator-Based**: Clean, intuitive command definition using `@Command` and `@Handler` decorators
- **Dual Command Types**: Support for both single commands (BasicCLI) and command groups (GenericCLI)
- **Beautiful Error Messages**: Rich, colorful error panels powered by rich-argparse
- **Async Support**: Full support for async/await in command handlers
- **Class-Attribute Parameters**: Define arguments as class attributes using `Parameter()` for BasicCLI
- **Handler Parameters**: Use method parameters for GenericCLI subcommands
- **Dependency Injection**: Commands are automatically registered via `useCLI` provider
- **Automatic Help Generation**: Built-in help system with beautiful formatting
- **Flexible Arguments**: Support for positional, optional, boolean flags, and more
- **Extensible**: Easy to add new commands and extend functionality

## Command Types

The CLI engine supports two fundamental command types:

### BasicCLI Commands
Single-action commands that execute one specific task. Perfect for standalone operations like displaying version information, building applications, or running initialization scripts.

**Pattern**: `ascender <command> [options]`

### GenericCLI Commands  
Multi-command groups that contain related subcommands. Ideal for organizing related functionality like code generation, database operations, or testing workflows.

**Pattern**: `ascender <group> <subcommand> [options]`

## Running Commands

There are two ways to invoke CLI in Ascender:

- Global CLI (tooling):
  - Pattern: `ascender [command]`
  - Examples:
    - `ascender new --name myapp --orm-mode tortoise`
    - `ascender serve`

- Local project wrapper (short form):
  - Pattern: `ascender run [command]`
  - Purpose: wraps local project entrypoints and CLI scripts (shorter than `poetry run python src/main.py`)
  - Examples:
    - `ascender run serve`
    - `ascender run tests`
    - `ascender run tests init`  (planned scaffolder: creates `src/tests/` samples and `pytest.ini`)

## Getting Started

To create your first command, you'll need to:

1. Import the necessary classes and decorators
2. Choose between BasicCLI or GenericCLI based on your needs
3. Define parameters appropriately for each type
4. Implement the required methods
5. Register your command using the `useCLI` provider

```python
from ascender.core.cli_engine import Command, Handler, BasicCLI, GenericCLI, Parameter, useCLI

# BasicCLI: Parameters are class attributes
@Command(name="hello", description="Say hello to the world")
class HelloCommand(BasicCLI):
    name: str = Parameter(
        "World", 
        description="Name to greet",
        names=["--name", "-n"]
    )
    
    def execute(self) -> None:
        print(f"Hello, {self.name}!")

# GenericCLI: Parameters are method arguments
@Command(name="greet", description="Greeting commands")
class GreetCommand(GenericCLI):
    
    @Handler("morning", description="Morning greeting")
    def morning(self, name: str = "World", **kwargs) -> None:
        print(f"Good morning, {name}!")
    
    @Handler("evening", description="Evening greeting")
    async def evening(self, name: str = "World", **kwargs) -> None:
        print(f"Good evening, {name}!")

# Register commands using useCLI provider
providers = [
    useCLI(HelloCommand),
    useCLI(GreetCommand),
]
```

## Architecture

The CLI system uses a modular, DI-integrated architecture:

- **Command Decorator (`@Command`)**: Handles command metadata and type detection
- **Handler Decorator (`@Handler`)**: Registers GenericCLI subcommands with async support
- **useCLI Provider**: Registers commands with the framework's DI system
- **Application Integration**: CLI engine is automatically configured in the Application
- **Command Protocols**: Define the interface for BasicCLI and GenericCLI
- **Parameter System**: Class attributes (BasicCLI) or method parameters (GenericCLI)
- **Rich Formatting**: Beautiful help messages and error panels using rich-argparse
- **Type Detection**: Automatic identification of command types

This design ensures that commands are easy to create, maintain, and extend while providing a consistent developer experience and seamless integration with the framework's dependency injection system.

## Next Steps

- Learn about [Command Types](command-types.md) to understand the differences between BasicCLI and GenericCLI
- Follow the [Creating Commands](creating-commands.md) guide to build your first command
- Explore [Examples](examples.md) to see real-world command implementations
