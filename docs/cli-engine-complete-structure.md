# Ascender Framework CLI Engine Structure Summary

## Overview

The Ascender Framework CLI engine supports two distinct command patterns:

1. **BasicCLI** - Single command execution
2. **GenericCLI** - Multi-command groups (subcommands)

## Command Structure

### BasicCLI Commands

**Pattern**: `ascender <command_name> [arguments]`

- **Single Action**: One `execute()` method handles all functionality
- **Arguments**: Supports both optional arguments (flags) and positional arguments
- **Use Cases**: Simple, standalone commands like `version`, `build`, `init`

```python
@Command(name="version", description="Display version")
class VersionCommand(BasicCLI):
    def execute(self, verbose: bool = False, **kwargs: Any) -> None:
        # Single command implementation
        pass
```

### GenericCLI Commands  

**Pattern**: `ascender <group_name> <subcommand> [arguments]`

- **Base Argument**: The name of the GenericCLI class (e.g., "generate")
- **Subcommand**: First positional argument specifying which method to call
- **Multiple Methods**: Each public method becomes a subcommand
- **Flexible Arguments**: Each subcommand can have its own arguments
- **Use Cases**: Related command groups like `generate`, `database`, `test`

```python
@Command(name="generate", description="Generate components")
class GenerateCommand(GenericCLI):
    def controller(self, name: str, path: str = "src/controllers", **kwargs: Any) -> None:
        # Subcommand: ascender generate controller MyController --path custom/path
        pass
        
    def service(self, name: str, interface: bool = False, **kwargs: Any) -> None:
        # Subcommand: ascender generate service MyService --interface
        pass
```

## Implementation Details

### Command Registration

The `@Command` decorator handles registration:

```python
@Command(
    name="command_name",        # Optional: defaults to lowercase class name
    description="Description",  # Used in help messages
    **kwargs                   # Additional options
)
```

### Automatic Detection

The decorator automatically detects command type:

- **BasicCLI**: Uses `issubclass(cls, BasicCLI)` check
- **GenericCLI**: Uses `issubclass(cls, GenericCLI)` check
- **Validation**: Raises error if class doesn't inherit from either

### Metadata Storage

Commands get metadata attributes:

```python
cls.__asc_command__ = {
    "name": "command_name",
    "description": "Command description", 
    "kind": "basic" | "generic",
    "parameters": [],
    **kwargs
}

# For GenericCLI only:
cls.__command_info__ = cls.__asc_command__  # Protocol compliance
```

## CLI Engine Processing

### Command Registration Flow

1. **Class Detection**: Engine iterates through command classes
2. **Kind Identification**: Checks `command_info['kind']`
3. **Parser Setup**:
   - **BasicCLI**: Adds direct argument to main parser
   - **GenericCLI**: Creates subparser with subcommands
4. **Method Discovery**: For GenericCLI, inspects public methods

### Argument Parsing

- **BasicCLI**: Direct argument parsing to `execute()` method
- **GenericCLI**: Two-level parsing (group → subcommand)

### Command Execution

1. **Parse Arguments**: `argparse` handles CLI input
2. **Command Lookup**: Find matching command class
3. **Instance Creation**: Instantiate command class
4. **Method Dispatch**:
   - **BasicCLI**: Call `execute(**args)`
   - **GenericCLI**: Call `method_name(**args)`

## Key Benefits

### Separation of Concerns
- **BasicCLI**: Simple, focused commands
- **GenericCLI**: Grouped, related functionality

### Type Safety
- Inheritance-based type checking
- Automatic validation of command structure

### Extensibility
- Easy to add new commands
- Consistent decorator pattern
- Flexible argument handling

### Developer Experience
- Clear command patterns
- Automatic help generation
- Method-based subcommand definition

## Example Command Structure

```
ascender
├── version (BasicCLI)
├── build (BasicCLI)
├── generate (GenericCLI)
│   ├── controller
│   ├── service
│   ├── module
│   └── repository
└── database (GenericCLI)
    ├── migrate
    ├── seed
    └── status
```

This structure provides a clear, maintainable, and extensible CLI framework that scales from simple single commands to complex multi-command workflows.
