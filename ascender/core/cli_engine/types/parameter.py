from argparse import ArgumentParser
from typing import Any

from ascender.core.cli_engine.types.undefined import UndefinedValue


class ParameterInfo:
    def __init__(
        self,
        name_or_flags: str | list[str] | None = None,
        default: Any | None = None,
        action: str | None = None,
        nargs: int | str | None = None,
        const: Any | None = None,
        dest: str | None = None,
        metavar: str | None = None,
        help: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.name_or_flags = name_or_flags if isinstance(name_or_flags, list) else [name_or_flags] if name_or_flags else []
        self.default = default
        self.action = action
        self.nargs = nargs
        self.const = const
        self.dest = dest
        self.metavar = metavar
        self.help = help
        self.kwargs = kwargs
        
        self._annotation: Any = UndefinedValue
    
    @property
    def annotation(self):
        return self._annotation
    
    @annotation.setter
    def annotation(self, value: Any):
        self._annotation = value
    
    def add_to_parser(
        self, 
        inspected_name: str, 
        parser: ArgumentParser,
        *,
        doc_string: str | None = None,
        **kwargs: Any
    ) -> None:
        """
        Adds the parameter information to the provided ArgumentParser instance.
        """
        if self.name_or_flags is not None:
            parser.add_argument(
                *(inspected_name, *self.name_or_flags),
                default=self.default,
                required=self.default is UndefinedValue,
                action=self.action or "store",
                nargs=self.nargs,
                const=self.const,
                dest=self.dest,
                metavar=self.metavar or inspected_name,
                help=self.help or doc_string,
                **self.kwargs
            )
    
    def __repr__(self) -> str:
        return f"ParameterInfo(name_or_flags={self.name_or_flags}, default={self.default}, action={self.action}, nargs={self.nargs}, const={self.const}, dest={self.dest}, metavar={self.metavar}, help={self.help})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParameterInfo):
            return False
        return (
            self.name_or_flags == other.name_or_flags and
            self.default == other.default and
            self.action == other.action and
            self.nargs == other.nargs and
            self.const == other.const and
            self.dest == other.dest and
            self.metavar == other.metavar and
            self.help == other.help and
            self.kwargs == other.kwargs
        )
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __copy__(self) -> 'ParameterInfo':
        raise TypeError("ParameterInfo cannot be copied.")
    
    def __deepcopy__(self, memo: dict) -> 'ParameterInfo':
        raise TypeError("ParameterInfo cannot be deep copied.")