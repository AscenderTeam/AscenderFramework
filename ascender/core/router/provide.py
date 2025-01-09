from typing import Sequence
from ascender.core.di.abc.base_injector import Injector
from ascender.core.di.injector import AscenderInjector
from ascender.core.di.interface.provider import Provider
from ascender.core.router.graph import RouterGraph
from ascender.core.router.interface.route import RouterRoute
from ascender.core.router.utils.from_controllers import handle_module_consumers
from ascender.core.struct.module_ref import AscModuleRef
from ascender.core.utils.module import load_module


def provideRouter(routes: Sequence[RouterRoute]) -> Provider:
    return {
        "provide": RouterGraph,
        "use_factory": lambda injector: RouterGraph(injector, routes),
        "deps": [Injector]
    }


def provideRouterFromControllers(module: type[AscModuleRef]) -> Provider:
    """
    Builds router graph using module and all controllers it has

    Args:
        module (type[AscModuleRef]): An AscModule with controllers in it's declarations
    """
    def router_graph_factory(module: type[AscModuleRef], injector: AscenderInjector):
        try:
            module = load_module(module)
        except RuntimeError:
            pass

        nodes = handle_module_consumers(module, injector)
        return RouterGraph(injector=injector, graph=[], load_from_nodes=True, _graph_nodes=nodes)
    

    return {
        "provide": RouterGraph,
        "use_factory": lambda injector: router_graph_factory(module, injector),
        "deps": [Injector]
    }