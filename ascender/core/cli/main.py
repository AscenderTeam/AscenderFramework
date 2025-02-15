from __future__ import annotations
import inspect

from sys import argv
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from ascender.core.cli.application import ContextApplication, ErrorHandler
from ascender.core.cli.injectable import Injectable
from ascender.core.cli.models import ArgumentCMD, ArgumentsFormat, OptionCMD
from ascender.core.errors.base import DeclaredBaseCliIsNotDefined, IncorrectCommandArgument
from rich import print as cprint
from rich.columns import Columns
from inspect import isfunction, unwrap

from ascender.core.registries.service import ServiceRegistry
if TYPE_CHECKING:
    from ascender.core.applications.application import Application
    

class BaseCLI:
    _config: dict[str, Any] = {}

    def get_arguments(self):
        result: list[ArgumentsFormat] = []
        # Iterate over annotated class variables
        for key, value in self.__class__.__dict__.get("__annotations__", {}).items():
            # Check if the variable is public and its type is among the specified types
            current_value = getattr(self, key, None)
            if not key.startswith('_'):
                # Optionally, get the current value of the variable
                result.append({"argument": key, "type": value,
                              "value": current_value, "is_ourobj": bool(type(current_value) in [ArgumentCMD, OptionCMD])})

        return result

    def callback(self, ctx: ContextApplication):
        """
        ## Callback function, all callbacks would be come here
        """
        pass


class GenericCLI:
    app_name: Optional[str] = None
    name_aliases: list[str] = []
    help: Optional[str] = None
    configs: Optional[dict] = None

    def get_method_arguments(self, _method: Callable, ignore: list[str]) -> list[ArgumentsFormat]:
        result: list[ArgumentsFormat] = []
        signature = inspect.signature(_method)

        for name, param in signature.parameters.items():
            if name in ignore:
                continue
            # Determine the type of the parameter
            param_type = param.annotation if param.annotation is not inspect.Parameter.empty else str

            # Determine the default value of the parameter
            default_value = param.default if param.default is not inspect.Parameter.empty else None

            if name == "self" and default_value is None:
                continue
            
            if name == "ctx":
                continue

            if param_type == bool and type(default_value) not in [OptionCMD, ArgumentCMD]:
                default_value = False
            result.append(
                {"argument": name, "type": param_type, "value": default_value, "is_ourobj": bool(type(default_value) in [ArgumentCMD, OptionCMD])})
        return result

    def get_methods(self) -> list[tuple[str, list[ArgumentsFormat]]]:
        result: list[tuple[str, list[ArgumentsFormat]]] = []

        for method_name, method in self.__class__.__dict__.items():
            if not isfunction(method):
                continue

            ignorable_params = []

            method_signature = inspect.signature(method)
            
            for name, value in method_signature.parameters.items():
                try:
                    if issubclass(value.annotation, Injectable):
                        ignorable_params.append(name)
                except:
                    pass

            if method_name != "__init__" and method_name:
                # Unwrap the method to get to the original function if it's wrapped by a decorator
                original_method = unwrap(method)
                # Get the arguments of the method
                arguments = self.get_method_arguments(original_method, ignorable_params)
                result.append((method_name, arguments))

        return result


    def __str__(self) -> str:
        return self.app_name


def console_command(name: Optional[str] = None, help: Optional[str] = None, **kwargs):
    """
    ## Console command.

    Command decorator for generic cli
    """
    def inner_wrapper(f):
        if hasattr(f, "alt_name"):
            f.alt_name = [*f.alt_name, name]
        else:
            f.alt_name = [name]
        f.help = help
        f.kwargs = kwargs
        
        @wraps(f)
        def decorator(*args, **kwargs):
            # if args:
            # return f(*args[1:], **kwargs)  # Skip the first argument
            
            return f(*args, **kwargs)
        return decorator

    return inner_wrapper

class CLI:
    app_name: str
    help: Optional[str]
    extra_arguments: Optional[dict]
    cli_list: List[BaseCLI] = []
    generic_cli_list: List[GenericCLI] = []
    handler_list: List[ErrorHandler] = []
    application: Application

    def __init__(self, application: Application, app_name: str, help: Optional[str] = None, **kwarg) -> None:
        self.app_name = app_name
        self.help = help
        self.extra_arguments = kwarg
        self.application = application

    def register_command(self, instance: BaseCLI):
        if issubclass(type(instance), BaseCLI):
            self.cli_list.append(instance)
            return

        raise DeclaredBaseCliIsNotDefined(instance.__class__.__name__)

    def register_handler(self, handler: ErrorHandler):
        if issubclass(type(handler), ErrorHandler):
            self.handler_list.append(handler)
            return

        raise DeclaredBaseCliIsNotDefined(handler.__class__.__name__)

    def register_generic_command(self, instance: GenericCLI):
        if issubclass(type(instance), GenericCLI):
            self.generic_cli_list.append(instance)
            return

        raise DeclaredBaseCliIsNotDefined(instance.__class__.__name__)

    def run(self):
        try:
            self.load_basecli()
            self.load_genericcli()
        except IndexError:
            self.handle_index_error()

    def load_basecli(self):
        cli_list = self.cli_list

        for cli in cli_list:

            if argv[1] == cli.__class__.__name__.lower():
                # Check if -h or --help is passed, if exception wasn't triggered and -h --help was called then print help
                # try:
                if argv in ["-h", "--help"]:
                    cprint("".join(
                        list(map(lambda c: c.get('argument', None),
                             cli.get_arguments()))
                    ))
                    return
                # except:
                    # pass

                arguments = cli.get_arguments()
                # if len(argv[2:]) > len(arguments):
                #     raise IncorrectCommandArgument(
                #         argv[1].lower(), argv[(len(argv) - 1) + (len(arguments) - 1)])

                # for index, item in enumerate(arguments):
                #     cmd_argument = argv[index]
                #     print(cmd_argument)

                #     if cmd_argument.isnumeric():
                #         cmd_argument = int(cmd_argument)

                #     if type(cmd_argument) != item["type"]:
                #         raise ValueError

                #     setattr(cli, item["argument"], cmd_argument)
                for argument in arguments:
                    # Check if argument has value, which will mean that it is optional

                    if f"--{argument['argument'].lower()}" in argv:
                        if argument['type'] == bool:
                            setattr(cli, argument["argument"], True)
                            continue

                        if argument["type"] == list:
                            cmd_argument = argv[argv.index(
                                f"--{argument['argument'].lower()}") + 1].split(",")
                            setattr(cli, argument["argument"], cmd_argument)
                            continue

                        cmd_argument = argv[argv.index(
                            f"--{argument['argument'].lower()}") + 1]

                        if cmd_argument.startswith("--"):
                            raise IncorrectCommandArgument(
                                argv[1].lower(), f"--{argument['argument'].lower()}")

                        if cmd_argument.isnumeric():
                            cmd_argument = int(cmd_argument)

                        if type(cmd_argument) != argument["type"]:
                            raise ValueError

                        setattr(cli, argument["argument"], cmd_argument)

                    if getattr(cli, argument["argument"], None) is None:
                        raise IncorrectCommandArgument(
                            argv[1].lower(), f"--{argument['argument'].lower()}")
                    # setattr(cli, argument["argument"], argv[2:][arguments.index(argument)])

                cli.callback(ContextApplication(application=self.application))

    def load_genericcli(self):
        cli_list = self.generic_cli_list
        for cli in cli_list:
            methods = cli.get_methods()
            for method in methods:
                try:
                    if "".join(argv[1:]).find(method["name"].lower().replace("_", "")) != -1:
                        # if argv[2] in ["-h", "--help"]:
                        #     cprint(method)
                        #     return
                        args = {}
                        arguments = method["args"][1:]
                        # if len(argv[2:]) > len(arguments):
                        #     raise IncorrectCommandArgument(
                        #         argv[1], argv[len(argv) - 1])

                        # for index, item in enumerate(arguments):
                        #     cmd_argument = argv[index + 2]

                        #     if cmd_argument.isnumeric():
                        #         cmd_argument = int(cmd_argument)

                        #     if type(cmd_argument) != item["type"]:
                        #         raise ValueError

                        #     args[item["argument"]] = cmd_argument
                        for argument in arguments:
                            if argument["argument"] == "ctx":
                                continue
                            # Check if argument has value, which will mean that it is optional
                            if f"--{argument['argument'].lower()}" in argv:
                                try:
                                    if argument['type'] == bool:
                                        args[argument["argument"]] = True
                                        continue

                                    if argument["type"] == list:
                                        cmd_argument = argv[argv.index(
                                            f"--{argument['argument'].lower()}") + 1].split(",")
                                        args[argument["argument"]
                                             ] = cmd_argument
                                        continue

                                    cmd_argument = argv[argv.index(
                                        f"--{argument['argument'].lower()}") + 1]
                                except IndexError:
                                    raise IncorrectCommandArgument(
                                        argv[1].lower(), f"--{argument['argument'].lower()}")

                                if cmd_argument.startswith("--"):
                                    raise IncorrectCommandArgument(
                                        argv[1].lower(), f"--{argument['argument'].lower()}")

                                if cmd_argument.isnumeric():
                                    cmd_argument = int(cmd_argument)

                                if type(cmd_argument) != argument["type"]:
                                    raise ValueError

                                args[argument["argument"]] = cmd_argument

                            if argument["type"] == bool:
                                args[argument["argument"]] = False
                                continue
                            # if getattr(cli, argument["argument"], None) is None:
                            #     raise IncorrectCommandArgument(
                            #         argv[1].lower(), f"--{argument['argument'].lower()}")
                        try:
                            func = getattr(cli, method["name"])
                            func(ctx=ContextApplication(
                                application=self.application), **args)

                        except TypeError as ex:
                            _req_attr = ex.args[0].split(
                                ' ')[-1].lower().replace("'", "")
                            raise IncorrectCommandArgument(
                                argv[1].lower(), f"--{_req_attr}")

                except IncorrectCommandArgument as ex:
                    raise ex

                except Exception as ex:
                    self.load_handlers(ex)
                    raise ex
                    # raise ex

    def load_handlers(self, exception: Exception):
        error_handler = ErrorHandler()
        error_handler.trigger_handlers(self.handler_list, exception)

    def handle_index_error(self):
        cprint("""
[bold red]Ascender Framework CLI[/bold red]
[bold red]------------------------[/bold red][yellow]
   ___   _________  _______   ____
  / _ | / __/ ___/ / ___/ /  /  _/
 / __ |_\ \/ /__  / /__/ /___/ /  
/_/ |_/___/\___/  \___/____/___/  [/yellow]

[bold red]Usage:[/bold red]
    [bold green]start.py[/bold green] [bold blue]<command>[/bold blue] [bold yellow]<args>[/bold yellow]
""")
        cols = Columns()

        commands_output = "[bold red]Available commands[/bold red]\n"
        arguments_output = "[bold red]Available arguments[/bold red]\n"

        for cli in self.cli_list:
            commands_output += f"    [bold green]{cli.__class__.__name__.lower()}[/bold green] "
            commands = cli.get_arguments()
            for name, arg_type in self.process_arguments(commands):
                if getattr(cli, name, None) is not None:
                    arguments_output += f"--[bold yellow]{name}[/bold yellow] [OPTIONAL {arg_type}] "
                    continue
                arguments_output += f"--[bold yellow]{name}[/bold yellow] [{arg_type}] "

            commands_output += "\n"
            arguments_output += "\n"

        for cli in self.generic_cli_list:
            commands = cli.get_methods()
            for command in commands:
                commands_output += f"    [bold green]{command['name'].replace('_', ' ')}[/bold green] "
                for name, arg_type in self.process_arguments(command["args"]):
                    arguments_output += f"--[bold yellow]{name}[/bold yellow] [{arg_type}] "

                commands_output += "\n"
                arguments_output += "\n"

        cols.add_renderable(commands_output)
        cols.add_renderable(arguments_output)
        cprint(cols)

    def process_arguments(self, arguments: list[dict[str, type]]):
        for argument in arguments:
            if argument["argument"] == "ctx" or argument["argument"] == "self":
                continue
            yield argument["argument"], argument["type"].__name__.upper()
