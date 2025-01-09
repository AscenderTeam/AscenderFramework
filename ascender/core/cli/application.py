from __future__ import annotations

from types import FunctionType
from typing import TYPE_CHECKING, Optional, Tuple, Union
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as cprint
from readchar import readchar
import sys

if TYPE_CHECKING:
    from ascender.core.applications.application import Application


class ContextApplication:
    console: Console

    def __init__(self, application: Application, emoji: bool = True) -> None:
        self.console = Console(emoji=emoji)
        self.application = application

    def console_print(self, message: Optional[str] = "", color: Optional[Union[str, Tuple[int]]] = None, table: Optional[Table] = None, panel: Optional[Panel] = None, **kwargs):
        """
        ## Console print

        Send message to console, respond to command.
        Use markdown like [green][/green] or [bold][/bold] for colors

        Args:
            message (Optional[str], optional): Message string which will be sended at response of this command. Defaults to "".
            color (Optional[Union[str, Tuple[int]]], optional): HEX or RGB color which will be colored message. Defaults to None.
            table (Optional[Table], optional): Table if needed. Defaults to None.
        """

        cprint(message, **kwargs)

        if table:
            cprint(table)

        if panel:
            cprint(panel)

    def console_pause(self, msg: Optional[str] = "Press any key to exit...", key: Optional[str] = None):
        """
        ## Console pause.

        After command execution wait until user presses key to exit the cli

        Args:
            msg (Optional[str], optional): Message which would be displayed for the user. Defaults to "".
        """
        cprint(msg)

        if key:
            k = readchar()

            if k == key:
                sys.exit(0)
        else:
            k = readchar()

            if k:

                sys.exit(0)

    def console_key(self, callback: FunctionType):
        """
        ## Get console key

        If user presses any key. This will get it and pass to callback function

        Args:
            callback (FunctionType): Callback function.
        """
        key = readchar()

        return callback(self, key)

    def console_input(self, msg: Optional[str] = "",
                      password: bool = False, 
                      show_default: bool = True, show_choices: bool = True, **kwargs) -> str:
        """
        ## Console input

        Get input from user, will prompt user to respond with string

        Args:
            msg (Optional[str], optional): Message that will be displayed to user before prompting. Defaults to "".
            password (bool, optional): Defines whether to hide the contents of what user types or not. Defaults to False.
            show_default (bool, optional): Will be displayed the default value if user ain't going to pass any value. Defaults to True.
            show_choices (bool, optional): Displays choices (Y/n) showing what type of choice can user select. Defaults to True.
        """
        return Prompt.ask(msg, console=self.console, password=password, show_default=show_default, show_choices=show_choices, **kwargs)
    
    def console_confirm(self, msg: Optional[str] = "", **kwargs) -> bool:
        """
        ## Console confirm

        Ask user to confirm anything from terminal session
        example:
        ```bash
        $ Are you sure you want to delete this file? (Y/n): {user input}
        ```

        Args:
            msg (Optional[str], optional): Message that will be displayed to user before confirming. Defaults to "".

        Returns:
            bool: If user confirms it will return True, otherwise False
        """
        return Confirm.ask(msg, console=self.console, **kwargs)


class Emoji:
    SMILE = {":smile:", ""}


class ErrorHandler:
    current_error: Exception

    def trigger_handler(self, exception: Exception):
        extra_args = exception.__class__.__dict__.get("handler_args", None)

        if extra_args:
            return self.on_command_error(ContextApplication(), exception, **extra_args)

        return self.on_command_error(ContextApplication(), exception)

    def trigger_handlers(self, handlers, exception: Exception):
        for handler in handlers:
            handler.trigger_handler(exception)

        return

    def on_command_error(self, ctx: ContextApplication, error: Exception, **kwargs):
        pass
