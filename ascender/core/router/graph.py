from __future__ import annotations
from typing import TYPE_CHECKING, MutableSequence, Sequence
from ascender.core.di.injector import AscenderInjector
from ascender.core.router.interface.route import RouterRoute
from ascender.core.router.router import RouterNode

if TYPE_CHECKING:
    from ascender.core.applications.application import Application


class RouterGraph:
    graph_nodes: MutableSequence[RouterNode]
    
    def __init__(
        self,
        injector: AscenderInjector,
        graph: Sequence[RouterRoute],
        *,
        load_from_nodes: bool = False,
        _graph_nodes: MutableSequence[RouterNode] = []
    ) -> None:
        self.injector = injector
        self.graph = graph
        self.load_from_nodes = load_from_nodes
        self.graph_nodes = _graph_nodes
    
    def create_router_graph(self, application: Application):
        """
        Instantiates all routes and runs them.
        Also it includes router into `FastAPI` one by one

        Args:
            application (Application): Main Application object
        """
        if self.load_from_nodes:
            for node in self.graph_nodes:
                # Include router into host
                application.app.include_router(node.router)
        else:
            for route in self.graph:
                _node = RouterNode(route, self.injector)
                
                # Include router into host
                application.app.include_router(_node.router)
                self.graph_nodes.append(_node)