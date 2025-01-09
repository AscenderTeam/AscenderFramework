from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ascender.core.struct.controller import Controller


class ControllerRef:
    __controller__: "Controller"