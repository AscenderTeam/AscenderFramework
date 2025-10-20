# Command Registration

Once you've created your CLI commands, you need to register them with the framework to make them available to users. The Ascender Framework uses a provider-based registration system that integrates seamlessly with its dependency injection container.

## The useCLI Provider

Commands are registered using the `useCLI` provider function, which integrates them into the framework's DI system. The framework's Application class automatically collects and configures all registered CLI commands.

### Basic Registration

Import and use the `useCLI` provider:

```python
from ascender.core.cli_engine import useCLI
from ascender.core import Provider
from myapp.commands import VersionCommand, BuildCommand

# Register commands as providers
providers: list[Provider] = [
    useCLI(VersionCommand),
    useCLI(BuildCommand),
]
```

## Module-Level Registration

### In Your Application Module

Register commands in your application's root module:

```python
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.cli_engine import useCLI
from myapp.commands import VersionCommand, BuildCommand, DeployCommand

class AppModule(AscModuleRef):
    providers = [
        # Other providers...
        useCLI(VersionCommand),
        useCLI(BuildCommand),
        useCLI(DeployCommand),
    ]
```
        module_name = f"{package_path}.{name}"
        module = importlib.import_module(module_name)
        
        # Find command classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, (BasicCLI, GenericCLI)) and
                hasattr(attr, '__asc_command__')):
                commands.append(attr)
    
    return commands

# Usage
commands = discover_commands('myapp.commands')
cli_engine = CLIEngine()
cli_engine.process_commands(commands)
```

## Integration Patterns

### Application Integration

Integrate the CLI engine into your main application:

```python
# main.py
import sys
from ascender.core.cli_engine import CLIEngine
from myapp.commands import discover_all_commands

def create_cli() -> CLIEngine:
    """Create and configure the CLI engine."""
    cli_engine = CLIEngine(
        description="MyApp - Development Tools",
        usage="myapp <command> [options]"
    )
    
    # Register commands
    commands = discover_all_commands()
    cli_engine.process_commands(commands)
    
    return cli_engine

def main():
    """Main CLI entry point."""
    cli_engine = create_cli()
    
    try:
        # Parse and execute commands
        result = cli_engine.parse_and_execute(sys.argv[1:])
        sys.exit(result or 0)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        ### Organizing Multiple Commands

For applications with many commands, organize them by feature:

```python
from ascender.core.cli_engine import useCLI
from myapp.commands import (
    # BasicCLI commands
    VersionCommand,
    BuildCommand,
    DeployCommand,
    TestCommand,
    
    # GenericCLI command groups
    GenerateCommand,
    DatabaseCommand,
    DevCommand,
)

# Group providers by functionality
cli_providers = [
    # Basic utility commands
    useCLI(VersionCommand),
    useCLI(BuildCommand),
    useCLI(TestCommand),
    
    # Deployment commands
    useCLI(DeployCommand),
    
    # Code generation
    useCLI(GenerateCommand),
    
    # Database management
    useCLI(DatabaseCommand),
    
    # Development tools
    useCLI(DevCommand),
]

class AppModule(AscModuleRef):
    providers = [
        *cli_providers,
        # ... other providers
    ]
```

## Complete Application Example

Here's a complete example showing command registration in a real application:

```python
# src/app_module.py
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.cli_engine import useCLI

# Import your commands
from src.commands.version import VersionCommand
from src.commands.build import BuildCommand
from src.commands.generate import GenerateCommand
from src.commands.database import DatabaseCommand

class AppModule(AscModuleRef):
    """Main application module."""
    
    imports = []
    
    controllers = [
        # Your controllers here
    ]
    
    providers = [
        # CLI Commands
        useCLI(VersionCommand),
        useCLI(BuildCommand),
        useCLI(GenerateCommand),
        useCLI(DatabaseCommand),
        
        # Other providers...
    ]
```

```python
# src/main.py
from ascender.core.applications.create_application import createApplication
from src.app_module import AppModule

# Create application with CLI support
app = createApplication(app_module=AppModule)

# The framework handles CLI execution automatically
# when run in CLI mode (via `ascender` command)
```
```

### Framework Integration

For framework-level integration:

```python
# ascender/cli/main.py

## Dependency Injection with Commands

Commands can receive dependencies through constructor injection:

```python
from ascender.core.cli_engine.decorators.command import Command
from ascender.core.cli_engine import GenericCLI, Handler
from ascender.common.injectable import Injectable
from myapp.services.generator_service import GeneratorService

@Injectable()
@Command(name="generate", description="Generate application components")
class GenerateCommand(GenericCLI):
    def __init__(self, generator_service: GeneratorService):
        self.generator_service = generator_service
    
    @Handler("controller", "c", description="Generate a controller")
    def controller(self, name: str, **kwargs) -> None:
        result = self.generator_service.generate_controller(name)
        print(f"Generated controller: {result}")
    
    @Handler("service", "s", description="Generate a service")
    def service(self, name: str, **kwargs) -> None:
        result = self.generator_service.generate_service(name)
        print(f"Generated service: {result}")
```

Register both the command and its dependencies:

```python
from ascender.core.cli_engine import useCLI
from myapp.commands.generate import GenerateCommand
from myapp.services.generator_service import GeneratorService

class AppModule(AscModuleRef):
    providers = [
        GeneratorService,
        useCLI(GenerateCommand),
    ]
```

## Project Structure Recommendation

Organize your CLI commands in a dedicated directory:

```
myapp/
├── src/
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── version.py      # BasicCLI commands
│   │   ├── build.py
│   │   ├── deploy.py
│   │   ├── generate.py     # GenericCLI commands
│   │   └── database.py
│   ├── services/
│   │   └── ...
│   ├── app_module.py       # Register commands here
│   └── main.py
└── cli.py                  # Entry point (if needed)
```

Example `__init__.py` to export all commands:

```python
# src/commands/__init__.py
from .version import VersionCommand
from .build import BuildCommand
from .deploy import DeployCommand
from .generate import GenerateCommand
from .database import DatabaseCommand

__all__ = [
    'VersionCommand',
    'BuildCommand',
    'DeployCommand',
    'GenerateCommand',
    'DatabaseCommand',
]
```

## Best Practices

1. **Use useCLI Provider**: Always register commands via `useCLI()` - never instantiate CLI commands manually
2. **Group Related Commands**: Use GenericCLI to group related subcommands together
3. **Dependency Injection**: Inject services into commands rather than creating instances directly
4. **Descriptive Names**: Use clear, descriptive names for commands and subcommands
5. **Help Text**: Always provide descriptions for commands and handlers
6. **Module Organization**: Keep commands in a dedicated `commands/` directory
7. **Type Hints**: Use type hints for all command parameters
8. **Documentation**: Add docstrings to command classes and methods

## Verification

After registering commands, verify they're available:

```bash
# Show all available commands
ascender --help

# Show command-specific help
ascender build --help
ascender generate --help

# Show subcommand help
ascender generate controller --help
```

## Next Steps

- Learn about [Creating Commands](creating-commands.md) to build your own CLI commands
- Explore [Command Types](command-types.md) to understand BasicCLI vs GenericCLI
- See [Examples](examples.md) for real-world command implementations
`````markdown
## Command Discovery Strategies

### Directory-Based Discovery

Organize commands by directory structure:

```
myapp/
├── commands/
│   ├── __init__.py
│   ├── basic/
│   │   ├── __init__.py
│   │   ├── version.py
│   │   └── build.py
│   └── groups/
│       ├── __init__.py
│       ├── generate.py
│       └── database.py
└── cli.py
```

```python
# myapp/commands/__init__.py
from .basic.version import VersionCommand
from .basic.build import BuildCommand
from .groups.generate import GenerateCommand
from .groups.database import DatabaseCommand

__all__ = [
    'VersionCommand',
    'BuildCommand', 
    'GenerateCommand',
    'DatabaseCommand',
]

def get_all_commands():
    """Get all available commands."""
    return [
        VersionCommand,
        BuildCommand,
        GenerateCommand, 
        DatabaseCommand,
    ]
```

### Plugin-Based Discovery

For plugin architectures:

```python
# myapp/cli/registry.py
class CommandRegistry:
    """Registry for CLI commands."""
    
    def __init__(self):
        self._commands = []
    
    def register(self, command_class):
        """Register a command class."""
        if hasattr(command_class, '__asc_command__'):
            self._commands.append(command_class)
        else:
            raise ValueError(f"Invalid command class: {command_class}")
    
    def register_module(self, module):
        """Register all commands from a module."""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                hasattr(attr, '__asc_command__')):
                self.register(attr)
    
    def get_commands(self):
        """Get all registered commands."""
        return self._commands.copy()

# Usage
registry = CommandRegistry()
registry.register(VersionCommand)
registry.register_module(myapp.commands.generate)

cli_engine = CLIEngine()
cli_engine.process_commands(registry.get_commands())
```

## Configuration Management

### Environment-Based Configuration

Configure CLI behavior based on environment:

```python
import os
from ascender.core.cli_engine import CLIEngine

def create_cli_for_environment() -> CLIEngine:
    """Create CLI engine based on environment."""
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        # Production CLI - minimal commands
        from myapp.commands.production import ProductionCommands
        commands = ProductionCommands.get_safe_commands()
    elif env == 'development':
        # Development CLI - all commands
        from myapp.commands import get_all_commands
        commands = get_all_commands()
    else:
        # Testing CLI - test-specific commands
        from myapp.commands.testing import TestingCommands
        commands = TestingCommands.get_test_commands()
    
    cli_engine = CLIEngine(
        description=f"MyApp CLI ({env} mode)"
    )
    cli_engine.process_commands(commands)
    
    return cli_engine
```

### Feature Flag Integration

Control command availability with feature flags:

```python
class ConditionalCommandRegistry:
    """Registry that respects feature flags."""
    
    def __init__(self, feature_flags: dict):
        self.feature_flags = feature_flags
        self._commands = []
    
    def register_if_enabled(self, command_class, feature_flag: str):
        """Register command only if feature flag is enabled."""
        if self.feature_flags.get(feature_flag, False):
            self._commands.append(command_class)
    
    def get_commands(self):
        return self._commands

# Usage
feature_flags = {
    'experimental_commands': True,
    'debug_commands': False,
}

registry = ConditionalCommandRegistry(feature_flags)
registry.register_if_enabled(ExperimentalCommand, 'experimental_commands')
registry.register_if_enabled(DebugCommand, 'debug_commands')
```

## Error Handling

### Registration Error Handling

Handle registration errors gracefully:

```python
def safe_register_commands(cli_engine: CLIEngine, commands: list):
    """Safely register commands with error handling."""
    successful = []
    failed = []
    
    for command_class in commands:
        try:
            # Validate command
            if not hasattr(command_class, '__asc_command__'):
                raise ValueError(f"Invalid command: {command_class}")
            
            # Register command
            cli_engine.process_commands([command_class])
            successful.append(command_class)
            
        except Exception as e:
            print(f"Warning: Failed to register {command_class.__name__}: {e}")
            failed.append((command_class, e))
    
    print(f"Registered {len(successful)} commands successfully")
    if failed:
        print(f"Failed to register {len(failed)} commands")
    
    return successful, failed
```

### Runtime Error Handling

Handle command execution errors:

```python
def main():
    """Main CLI with comprehensive error handling."""
    try:
        cli_engine = create_cli()
        result = cli_engine.parse_and_execute()
        sys.exit(result or 0)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(130)  # Standard exit code for SIGINT
        
    except SystemExit:
        raise  # Don't catch sys.exit()
        
    except Exception as e:
        if os.getenv('DEBUG'):
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}")
        sys.exit(1)
```

## Best Practices

### Command Organization

1. **Group Related Commands**: Use GenericCLI for related functionality
2. **Consistent Naming**: Use clear, consistent command names
3. **Logical Hierarchy**: Organize commands in a logical structure

### Registration Strategy

1. **Lazy Loading**: Load commands only when needed
2. **Error Resilience**: Handle registration failures gracefully
3. **Feature Flags**: Use feature flags for experimental commands
4. **Environment Awareness**: Adapt command availability to environment

### Performance Considerations

1. **Avoid Heavy Imports**: Import command modules lazily
2. **Command Discovery Caching**: Cache discovered commands
3. **Minimal Registration**: Only register commands that are actually available

## Next Steps

- Explore [Examples](examples.md) for complete command implementations
- Learn about advanced CLI engine features and customization options
- Check out the framework's built-in commands for inspiration
