from inspect import Parameter, signature
from typing import List, Dict, Set, Any, cast
from collections import defaultdict

from ascender.core.di.utils.providers import is_factory_provider, is_static_class_provider, is_value_provider

from ..interface.provider import FactoryProvider, Provider, StaticClassProvider


def extract_dependencies_from_class(cls: type) -> List[Any]:
    """Extracts dependencies from the constructor of a class."""
    deps = []
    constructor = getattr(cls, "__init__", None)
    if constructor:
        sig = signature(constructor)
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            if param.annotation != Parameter.empty:
                deps.append(param.annotation)
            else:
                raise ValueError(f"Parameter '{name}' in {cls} lacks a type annotation.")
    return deps


def build_dependency_graph(providers: List[Provider]) -> Dict[Any, Set[Any]]:
    """
    Builds a dependency graph from the list of providers.
    """
    graph = defaultdict(set)

    def add_dependencies(token: Any, dependencies: List[Any]):
        for dep in dependencies:
            graph[dep].add(token)  # Reverse the edge direction
        if token not in graph:
            graph[token] = set()  # Ensure token is present in the graph

    for provider in providers:
        if is_factory_provider(provider):
            token = cast(FactoryProvider, provider)["provide"]
            dependencies = provider.get("deps", [])
            add_dependencies(token, dependencies)

        elif is_static_class_provider(provider):
            token = cast(StaticClassProvider, provider)["provide"]
            dependencies = provider.get("deps", [])
            add_dependencies(token, dependencies)

        elif isinstance(provider, type):  # TypeProvider
            token = provider
            dependencies = extract_dependencies_from_class(provider)
            # Extract dependencies from constructor for TypeProvider
            add_dependencies(token, dependencies)

        # ValueProvider doesn't participate in the graph
        elif is_value_provider(provider):
            token = provider["provide"]
            add_dependencies(token, [])

        else:
            raise ValueError(f"Unknown provider type: {provider}")

        # Ensure token is in the graph even if it has no dependencies
        if token not in graph:
            graph[token] = set()

    return graph


def topological_sort(graph: Dict[Any, Set[Any]]) -> List[Any]:
    """
    Performs topological sorting on the dependency graph.
    """
    in_degree = {node: 0 for node in graph}
    for dependencies in graph.values():
        for dep in dependencies:
            in_degree[dep] += 1

    # Print initial in-degree map
    print("Initial in-degree:", in_degree)

    # Queue for nodes with no incoming edges
    queue = [node for node, degree in in_degree.items() if degree == 0]
    print("Initial queue:", queue)

    sorted_order = []

    while queue:
        current = queue.pop(0)
        sorted_order.append(current)

        print(f"Processing node: {current}")
        print(f"Queue before adding neighbors: {queue}")

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

        print(f"Queue after adding neighbors: {queue}")
        print(f"Sorted order so far: {sorted_order}")

    # Detect cycles
    if len(sorted_order) != len(graph):
        raise ValueError("Graph has a cycle. Topological sort is not possible.")

    return sorted_order
