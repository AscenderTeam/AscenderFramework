from typing import Callable, TypeVar
from ascender.common.module import AscModule
from ascender.core.cli.main import BaseCLI, GenericCLI
from ascender.core.cli.processor import CLI


Module = TypeVar("Module")


class CLIProvider:
    def __init__(
        self,
        generic_cli: list[type[GenericCLI]],
        base_cli: dict[str, type[BaseCLI]],
        *,
        register_manually: Callable[[CLI], None] = lambda c: None
    ):
        self.generic_clis = generic_cli
        self.base_clis = base_cli
        self.manual_registration = register_manually
    
    def invoke(self, cli: CLI):
        for gc in self.generic_clis:
            cli.register_generic(gc)
        
        for name, bc in self.base_clis.items():
            cli.register_base(name, bc)
        
        self.manual_registration(cli)
    
    @classmethod
    def fromModule(
        cls, module: Module
    ):
        # Handle module first
        module.bootstrap()

        generic_clis: list[GenericCLI] = []
        base_clis: dict[str, BaseCLI] = {}

        # Handle module scopes and get the generic / basic clis
        for t, o in module._module_scope.items():
            if issubclass(t, GenericCLI):
                generic_clis.append(o)
                continue

            if issubclass(t, BaseCLI):
                base_clis[t.__name__.lower().removesuffix("cli")] = o
                continue
        
        return cls(generic_cli=generic_clis, base_cli=base_clis)