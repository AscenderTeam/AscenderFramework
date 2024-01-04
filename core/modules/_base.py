from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.application import Application


class Module:
    app: Application

    def run(self):
        raise NotImplementedError("Module is not implemented")
    
    def down(self):
        raise NotImplementedError("Module is not implemented")
