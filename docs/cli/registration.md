# Command Registration

Once you've created your CLI commands, register them with the framework so they become available to users. Registration goes through the framework's dependency injection system — there is one canonical way to do it: the `useCLI` provider.

## The `useCLI` Provider

`useCLI` wraps a command class into a DI provider. During application creation, the framework collects every registered command and wires it into the CLI engine — alongside the built-ins (`serve`, `generate`, `build`, `tests`).

```python
from ascender.core.cli_engine import useCLI
from commands.version import VersionCommand
from commands.deploy import DeployCommand

providers = [
    useCLI(VersionCommand),
    useCLI(DeployCommand),
]
```

!!! warning "Never instantiate command classes manually"
    Always pass the **class** to `useCLI(...)`. The framework instantiates it through DI, which is also what makes constructor injection work.

## Where to Register

### In the bootstrap (provider-based apps)

```python title="src/bootstrap.py" hl_lines="9 10"
from ascender.core.cli_engine import useCLI
from ascender.core.types import IBootstrap
from commands.version import VersionCommand
from commands.deploy import DeployCommand

appBootstrap: IBootstrap = {
    "providers": [
        # ... router, database, docs providers ...
        useCLI(VersionCommand),
        useCLI(DeployCommand),
    ]
}
```

### In a module (module-based apps)

```python title="src/app_module.py" hl_lines="8 9"
from ascender.core import AscModule
from ascender.core.cli_engine import useCLI

@AscModule(
    imports=[],
    declarations=[],
    providers=[
        useCLI(VersionCommand),
        useCLI(DeployCommand),
    ],
    exports=[],
)
class AppModule: ...
```

## Dependency Injection in Commands

Commands receive dependencies through constructor injection, exactly like controllers and services:

```python title="src/commands/generate.py"
from ascender.core.cli_engine import Command, Handler, GenericCLI
from services.generator_service import GeneratorService

@Command(name="generate", description="Generate application components")
class GenerateCommand(GenericCLI):
    def __init__(self, generator_service: GeneratorService):
        self.generator_service = generator_service

    @Handler("controller", "c", description="Generate a controller")
    def controller(self, name: str, **kwargs) -> None:
        result = self.generator_service.generate_controller(name)
        print(f"Generated controller: {result}")
```

Register **both** the command and its dependencies in the same scope:

```python
providers = [
    GeneratorService,            # the dependency
    useCLI(GenerateCommand),     # the command that consumes it
]
```

!!! tip
    If the service is already decorated with `@Injectable(provided_in="root")`, you don't need to list it again — only the `useCLI(...)` entry is required.

## Running Registered Commands

Project commands run through the local project wrapper:

```bash
ascender run <command> [subcommand] [options]
```

```bash
ascender run version --verbose
ascender run generate controller users
ascender run deploy upload ./dist --dest /var/www
```

## Recommended Project Layout

Keep commands in a dedicated directory and re-export them from its `__init__.py`:

```
src/
├── commands/
│   ├── __init__.py        # re-exports all command classes
│   ├── version.py         # BasicCLI commands
│   ├── deploy.py
│   └── generate.py        # GenericCLI groups
├── services/
│   └── ...
├── bootstrap.py           # useCLI(...) registrations live here
└── main.py
```

```python title="src/commands/__init__.py"
from .version import VersionCommand
from .deploy import DeployCommand
from .generate import GenerateCommand

__all__ = ["VersionCommand", "DeployCommand", "GenerateCommand"]
```

This keeps `bootstrap.py` to a single tidy import:

```python
from commands import VersionCommand, DeployCommand, GenerateCommand
```

## Verifying Registration

After registering, confirm your commands show up:

```bash
ascender run --help              # list all project commands
ascender run deploy --help       # command/group help
ascender run deploy upload --help  # subcommand help
```

If a command is missing from `--help`, check that:

1. The class is decorated with `@Command(...)` — undecorated classes are ignored.
2. `useCLI(YourCommand)` is present in an active `providers` list.
3. The module defining the command is actually imported by your bootstrap (an unimported file never registers anything).

## Best Practices

1. **Use `useCLI`** — never instantiate CLI commands manually.
2. **Group related subcommands** in a `GenericCLI` instead of many one-off commands.
3. **Inject services** rather than constructing them inside commands.
4. **Always provide descriptions** for commands and handlers — they become the help text.
5. **Keep commands thin**: parsing and presentation in the command, business logic in services.

## Next Steps

- Learn about [Creating Commands](creating-commands.md) to build your own CLI commands
- Explore [Command Types](command-types.md) to understand BasicCLI vs GenericCLI
- See [Examples](examples.md) for real-world command implementations
