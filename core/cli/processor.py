from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

import rich_click as click
from core.cli.application import ContextApplication
from core.cli.loaders.base_loader import LoaderBaseCLI
from core.cli.loaders.generic_loader import GenericLoader
from core.cli.main import GenericCLI, BaseCLI
from rich.traceback import install

if TYPE_CHECKING:
    from core.application import Application


class CLI:

    def __init__(self, 
                 application: Application,
                 *,
                 app_name: str = "AscenderCLI",
                 generic_clis: list[GenericCLI] = [], base_clis: list[tuple[str, BaseCLI]] = [],
                 callback: Optional[Callable[[ContextApplication], None]] = None) -> None:
        self.app_name = app_name
        self.generic_clis = generic_clis
        self.base_clis = base_clis
        self.callback = callback
        self.application = application

        install(max_frames=20, suppress=["click"])

    def register_generic(self, generic_cli: GenericCLI) -> None:
        if generic_cli in self.generic_clis:
            raise ValueError(f"GenericCLI {generic_cli} already registered")
        
        if not isinstance(generic_cli, GenericCLI):
            raise ValueError(f"GenericCLI {generic_cli} is not a GenericCLI instance")

        self.generic_clis.append(generic_cli)
    
    def register_base(self, name: str, base_cli: BaseCLI) -> None:
        if base_cli in self.base_clis:
            raise ValueError(f"BaseCLI Instance `{base_cli.__class__.__name__}` is already registered")
        
        if not isinstance(base_cli, BaseCLI):
            raise ValueError(f"Instance `{base_cli.__class__.__name__}` is not a BaseCLI instance")
        
        self.base_clis.append((name, base_cli))

    def load_basic(self, main_group: click.Group) -> None:
        for name, base_cli in self.base_clis:
            command = LoaderBaseCLI(base_cli, self.application, name, lambda: print("test")).run()
            main_group.add_command(command)
    
    def load_generic(self, main_group: click.Group) -> None:
        for generic_cli in self.generic_clis:
            group = GenericLoader(generic_cli, self.application,
                                  callback=self.callback)
            main_group.add_command(group.run(), self.app_name if generic_cli.app_name is None else None)

    def run(self) -> None:
        main_group = click.RichGroup()

        self.load_basic(main_group)
        self.load_generic(main_group)

        main_group()