from typing import Any, Optional, TypedDict
import click


class OptionCMD:
    def __init__(self, *names: str, default: Optional[Any] = None, 
                 ctype: type = str, help: Optional[str] = None,
                 is_flag: bool = False, flag_value: Optional[Any] = None, 
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
        if not self.additonal_kwargs.get("exclude_formatting_name", False):
            argument_name = argument_name.replace("_", "-")

        return click.Option([f"--{argument_name}", *self.names], default=self.default, 
                            is_flag=self.is_flag, 
                            flag_value=self.flag_value,
                            type=self.type, 
                            help=self.help, 
                            required=self.required, 
                            **self.additonal_kwargs)

    def __repr__(self) -> str:
        return f"OptionCMD(default={self.default}, names={self.names}, type={self.type}, help={self.help}, required={self.required})"


class ArgumentCMD:
    def __init__(self, default: Optional[Any] = None, *, name: Optional[str] = None, 
                 ctype: Optional[any] = None, help: Optional[str] = None, 
                required: bool = False, **kwargs) -> None:
        self.default = default if default is not None else CommandNull()
        self.name = name
        self.type = ctype
        self.help = help
        self.required = required
        self.additional_kwargs = kwargs
    
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


class CommandNull:
    pass