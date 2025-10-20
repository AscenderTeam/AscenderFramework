from argparse import ArgumentParser
from typing import Any, Mapping

from ascender.core.cli_engine.types.undefined import UndefinedValue


class ParameterInfo:
    def __init__(
        self,
        name_or_flags: str | list[str] | None = None,
        default: Any | None = None,
        default_factory: Any | None = None,
        action: str | None = None,
        nargs: int | str | None = None,
        const: Any | None = None,
        dest: str | None = None,
        metavar: str | None = None,
        help: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.name_or_flags = name_or_flags if isinstance(name_or_flags, list) else [name_or_flags] if name_or_flags else []
        self.default = default if default is not UndefinedValue else (default_factory() if default_factory is not None else UndefinedValue)
        self.action = action
        self.nargs = nargs
        self.const = const
        self.dest = dest  # Keep the explicitly provided dest, or None if not provided
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
        doc_string: str | None = None
    ) -> None:
        """
        Adds the parameter information to the provided ArgumentParser instance.
        """
        if self.name_or_flags is not None:
            dest = self.dest if self.dest is not None else inspected_name

            # if is psositional argument, remove dest
            if not any(flag.startswith("-") for flag in self.name_or_flags):
                dest = None
            
            action = self.action
            if action is None and isinstance(self.default, bool):
                action = "store_true" if not self.default else "store_false"

            args: Mapping[str, Any] = {
                "help": self.help or doc_string,
            }
            
            if dest is not None:
                args["dest"] = dest
                args["required"] = self.default == UndefinedValue
            
            if action in ("store_true", "store_false"):
                args["action"] = action
            
            else:
                args.update({
                    "default": self.default,
                    "action": action or "store",
                    "metavar": self.metavar or inspected_name,
                })
                if self.nargs is not None:
                    args["nargs"] = self.nargs
                if self.const is not None:
                    args["const"] = self.const
            
            args.update(self.kwargs)
            parser.add_argument(*self.name_or_flags, **args)
    
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