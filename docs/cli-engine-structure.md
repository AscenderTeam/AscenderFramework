# Ascender Framework CLI Engine Structure

The Ascender Framework CLI engine supports two types of command structures:

## BasicCLI - Single Command

A `BasicCLI` command represents a single action that can be executed from the command line.

### Structure:
- **Inheritance**: Must inherit from `BasicCLI`
- **Implementation**: Must implement the `execute()` method
- **Arguments**: Can have optional arguments and positional arguments passed via `**kwargs`
- **Usage Pattern**: `ascender <command_name> [arguments]`

### Example:
```python
@Command(name="version", description="Display the version")
class VersionCommand(BasicCLI):
    def execute(self, verbose: bool = False, **kwargs: Any) -> None:
        if verbose:
            print("Ascender Framework v1.0.0 (detailed)")
        else:
            print("Ascender Framework v1.0.0")
```

**CLI Usage**: `ascender version --verbose`

## GenericCLI - Multi-Command Group

A `GenericCLI` command represents a group of related commands (subcommands).

### Structure:
- **Inheritance**: Must inherit from `GenericCLI`
- **Implementation**: Contains multiple methods, each representing a subcommand
- **Base Argument**: The name of the GenericCLI (e.g., "generate")
- **Subcommand**: First positional argument specifying which method to call
- **Additional Arguments**: Can have multiple positional and optional arguments
- **Usage Pattern**: `ascender <group_name> <subcommand> [arguments]`

### Example:
```python
@Command(name="generate", description="Generate project components")
class GenerateCommand(GenericCLI):
    def controller(self, name: str, path: str = "src/controllers", **kwargs: Any) -> None:
        print(f"Generating controller '{name}' in {path}")
        
    def service(self, name: str, interface: bool = False, **kwargs: Any) -> None:
        print(f"Generating service '{name}'")
```

**CLI Usage**: 
- `ascender generate controller UserController --path src/api/controllers`
- `ascender generate service UserService --interface`

## Command Registration

Both command types use the `@Command` decorator for registration:

```python
@Command(
    name="command_name",        # Optional: defaults to class name (lowercase)
    description="Description",  # Optional: used in help messages
    **kwargs                   # Additional command-specific options
)
class MyCommand(BasicCLI | GenericCLI):
    # Implementation
```

## Key Differences

| Aspect | BasicCLI | GenericCLI |
|--------|----------|------------|
| **Purpose** | Single action | Group of related actions |
| **Methods** | One `execute()` method | Multiple command methods |
| **CLI Pattern** | `ascender <cmd> [args]` | `ascender <group> <subcmd> [args]` |
| **Use Cases** | Version, build, init | Generate, database, test |

## Implementation Notes

1. **Method Detection**: The CLI engine automatically detects the command type based on inheritance
2. **Argument Parsing**: Both types support typed arguments with default values
3. **Help Generation**: Descriptions and method docstrings are used for auto-generated help
4. **Command Info**: The decorator adds `__asc_command__` metadata to the class
5. **Generic CLI Protocol**: GenericCLI also gets `__command_info__` for protocol compliance
