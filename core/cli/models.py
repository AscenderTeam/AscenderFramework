from typing import Tuple, TypeVar
from core.errors.base import IncorrectCommandArgument


class CMDArgumentLine:
    def __init__(self, name: str, vartype: type, default=None, required: bool = False) -> None:
        self.name = name
        self.vartype = vartype
        self.required = required
        self.value = default

    def set_value(self, value):
        """
        ## Set Value

        Determine value of variable

        Args:
            value (any): Value
        """
        self.value = value

    def get_value(self):
        """
        ## Get value

        Gets value determined on CLI.
        """
        if self.required and not self.value:
            raise IncorrectCommandArgument(self.name, None)

        return self.value


T = TypeVar("T", str, int)

ArgumentedCMD = Tuple[str, T]