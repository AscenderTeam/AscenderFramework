from typing import Optional, TypedDict
from rich.console import Console
from rich.markup import escape
import click


class OptionCMD:
    def __init__(self, *names: list[str], default: Optional[str] = None, 
                 ctype: type = str, help: Optional[str] = None,
                 is_flag: bool = False, flag_value: Optional[str] = None, 
                 required: bool = True, **kwargs) -> None:
        self.default = default
        self.names = names
        self.type = ctype
        self.is_flag = is_flag
        self.flag_value = flag_value
        self.help = help
        self.required = required
        self.additonal_kwargs = kwargs

        if required and default is not None:
            raise ValueError("You cannot have a default value and required=True")
    
    def parse(self, argument_name: str) -> click.Option:
        return click.Option([f"--{argument_name}", *self.names], default=self.default, type=self.type, help=self.help, required=self.required, **self.additonal_kwargs)

    def __repr__(self) -> str:
        return f"OptionCMD(default={self.default}, names={self.names}, type={self.type}, help={self.help}, required={self.required})"


class ArgumentCMD:
    def __init__(self, default: Optional[str] = None, *, name: Optional[str] = None, 
                 ctype: Optional[any] = None, help: Optional[str] = None, 
                required: bool = False) -> None:
        self.default = default
        self.name = name
        self.type = ctype
        self.help = help
        self.required = required
    
    def validate(self, value: any) -> bool:
        # TODO: Make a validator

        return True

    def __repr__(self) -> str:
        return f"ArgumentCMD(default={self.default}, name={self.name}, type={self.type}, help={self.help}, required={self.required})"
    

class ArgumentsFormat(TypedDict):
    argument: str
    type: type
    value: list | str | int | float | bool | OptionCMD | ArgumentCMD | None
    is_ourobj: bool