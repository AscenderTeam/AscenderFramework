# CLI API

The CLI API provides decorators and classes for building command-line interfaces.

## Core Components

### Decorators

Decorator for defining CLI commands.

::: ascender.core.cli_engine.Command
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__

::: ascender.core.cli_engine.Handler
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__


### Proxies of CLI command types

::: ascender.core.cli_engine.BasicCLI
    options:
      show_root_heading: true
      show_source: false
      members_order: source

::: ascender.core.cli_engine.GenericCLI
    options:
      show_root_heading: true
      show_source: false

### Parameters & Annotation Utilities

Each CLI argument can be configured as pure basic python annotations aren't enough for customizing CLI command.
So Ascender Framework provides a few Field metadata functions with which you can annotate your arguments and configure them.

::: ascender.core.cli_engine.Parameter
    options:
      show_root_heading: true
      show_source: false

::: ascender.core.cli_engine.BooleanParameter
    options:
      show_root_heading: true
      show_source: false

::: ascender.core.cli_engine.ConstantParameter
    options:
      show_root_heading: true
      show_source: false

::: ascender.core.cli_engine.types.undefined.UndefinedValue
    options:
      show_root_heading: true
      show_source: true



## See Also

- [CLI Overview](../cli/overview.md) - CLI system overview
- [Creating Commands](../cli/creating-commands.md) - Detailed command creation guide
- [Command Examples](../cli/examples.md) - More CLI examples
