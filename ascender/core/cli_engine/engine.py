from inspect import iscoroutinefunction
import sys
from typing import Any, Mapping, MutableMapping, Sequence
import asyncio

import rich_argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ascender.core.cli_engine.protos.generic_cli import GenericCLI
from ascender.core.cli_engine.protos.basic_cli import BasicCLI
from ascender.core.cli_engine.types.command_metadata import BasicMetadata_, GenericMetadata_
from ascender.core.cli_engine.utils.argparser import RichArgumentParser
from ascender.core.cli_engine.utils.valiidator import call_parsed_method, set_parsed_attr



class CLIEngine:
    def __init__(
        self,
        commands: Sequence[GenericCLI | BasicCLI] | None = None,
        usage: str | None = None,
        description: str | None = None
    ) -> None:
        """
        Ascender Framework's CLI Engine represents the command-line interface for the framework.
        It allows users to interact with the framework through command-line commands and parameters.
        
        Also providing them OOP-like interface to define their custom `ascender` commands.
        
        It consists of two main components:
        1. **BasicCLI**: These are the command-line basic classbased commands that can be executed directly only one command (with argument or not).
        2. **GenericCLI**: These are the generic commands that can be used to create groups of commands.
        """
        # Configure rich-argparse for beautiful output
        rich_argparse.RichHelpFormatter.styles["argparse.prog"] = "bold cyan"
        rich_argparse.RichHelpFormatter.styles["argparse.groups"] = "bold yellow"
        rich_argparse.RichHelpFormatter.styles["argparse.help"] = "dim"
        rich_argparse.RichHelpFormatter.styles["argparse.metavar"] = "bold magenta"
        
        self.parser = RichArgumentParser(
            "Ascender Framework CLI", 
            usage=usage,
            description=description,
            formatter_class=rich_argparse.RichHelpFormatter
        )
        # make subparsers optional at argparse level and show a friendly metavar in help
        self.command_subparsers = self.parser.add_subparsers(
            dest="command",
            metavar="command",
            help="Available commands",
            required=False,
        )

        self.command_map: MutableMapping[str, BasicCLI | GenericCLI] = {}

        if commands:
            self.process_commands(commands)

    def process_commands(self, commands: Sequence[BasicCLI | GenericCLI]) -> None:
        """
        Process and register CLI commands with the argument parser.
        
        Args:
            commands: Sequence of command instances decorated with @Command
        """
        
        for command_instance in commands:
            command_info: BasicMetadata_ | GenericMetadata_ | None = getattr(command_instance, "__asc_command__", None)
            if not command_info:
                continue
            if isinstance(command_info, BasicMetadata_):
                # BasicCLI command
                command_name = command_info.name or command_instance.__class__.__name__.lower()
                command_info.add_to_argparse(self.command_subparsers)

                self.command_map[command_name] = command_instance
                # map aliases to the same instance (forgot and that was pain)
                aliases = command_info.additional.get("aliases") if hasattr(command_info, "additional") else None
                if aliases:
                    if isinstance(aliases, str):
                        aliases = [aliases]
                    for alias in aliases:
                        self.command_map[alias] = command_instance
            
            elif isinstance(command_info, GenericMetadata_):
                # GenericCLI command
                command_name = command_info.name or command_instance.__class__.__name__.lower()
                command_info.add_to_argparse(self.command_subparsers)

                self.command_map[command_name] = command_instance
                # map aliases to the same instance (forgot and that was pain)
                aliases = command_info.additional.get("aliases") if hasattr(command_info, "additional") else None
                if aliases:
                    if isinstance(aliases, str):
                        aliases = [aliases]
                    for alias in aliases:
                        self.command_map[alias] = command_instance

    def execute_command(self, command_instance: Any, arguments: Mapping[str, Any]) -> Any:
        """
        Execute a command based on parsed arguments.
        
        Args:
            command_instance: The command instance to execute
            arguments: Parsed command line arguments
            
        Returns:
            Result of command execution
        """
        
        if isinstance(command_instance, BasicCLI):
            command_info = command_instance.__asc_command__
            
            # Set parameter values on the instance
            for key, value in arguments.items():
                if key in command_info.parameters:
                    set_parsed_attr(command_instance, key, value)

            return command_instance.execute()

        elif isinstance(command_instance, GenericCLI):
            command_info = command_instance.__asc_command__

            selected = arguments.get("subcommand")
            
            if not selected:
                console = Console()
                available = ", ".join(sorted(h.names[0] for h in command_info.parameters)) or "(no commands registered)"
                panel_text = Text.assemble(
                    ("No subcommand provided.\n\n", "bold white"),
                    ("Available subcommands: ", "bold"),
                    (available, "cyan"),
                    ("\n\nTry: ", "dim"),
                    ("ascender <command> <subcommand> --help", "bold cyan"),
                )
                console.print(Panel(panel_text, title="Error", border_style="red"))
                console.print()
                # self.parser.print_help()
                self.parser.exit(2)

            handler_info = None
            for h in command_info.parameters:
                if selected in getattr(h, "names", []) or selected == getattr(h, "_functionname", None):
                    handler_info = h
                    break

            if handler_info is None:
                raise ValueError(f"No valid subcommand found in arguments: {selected}")

            subcommand_args = {k: v for k, v in arguments.items() if k in handler_info.parameters}
            
            method = getattr(command_instance, handler_info._functionname)

            return call_parsed_method(method, subcommand_args)
        
        else:
            raise TypeError(f"Unknown command type: {type(command_instance)}")

    def parse_and_execute(self, argv: list[str] | None = None) -> Any:
        """
        Parse command line arguments and execute the appropriate command.
        
        Args:
            argv: Command line arguments (defaults to sys.argv)
            
        Returns:
            Result of command execution
        """
        args = self.parser.parse_args(argv)

        # If the user didn't provide any command, show a friendly rich error panel
        if getattr(args, "command", None) is None:
            console = Console()
            available = ", ".join(sorted(self.command_map.keys())) or "(no commands registered)"
            panel_text = Text.assemble(
                ("No command provided.\n\n", "bold white"),
                ("Available commands: ", "bold"),
                (available, "cyan"),
                ("\n\nTry: ", "dim"),
                ("ascender <command> --help", "bold cyan"),
            )
            console.print(Panel(panel_text, title="Error", border_style="red"))
            console.print()
            self.parser.print_help()
            self.parser.exit(2)

        command = self.command_map.get(args.command)
        if not command:
            console = Console()
            console.print(Panel(Text(f"Unknown command: {args.command}", style="bold white on red"), title="Error", border_style="red"))
            console.print()
            self.parser.print_help()
            self.parser.exit(2)

        return self.execute_command(command, vars(args))

    def __call__(self) -> Any:
        """
        Make the CLI engine callable for backward compatibility.
        """
        argv = sys.argv[1:]
        return self.parse_and_execute(argv)