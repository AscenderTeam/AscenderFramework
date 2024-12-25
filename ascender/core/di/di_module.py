import inspect
from typing import Any, TypeVar
from ascender.abstracts.factory import AbstractFactory
from ascender.abstracts.module import AbstractModule
from ascender.core.registries.service import ServiceRegistry


T = TypeVar("T")


class DIModule:
    _module_scope: dict[type[T | AbstractModule], T | AbstractModule] = {}
    _imported_modules: dict[type[T], T] = {}
    
    def get_dependencies(self, obj: Any):
        """
        Extracts the dependencies (constructor arguments) of a class.

        Args:
            cls (type): The class to analyze.

        Returns:
            list[type]: A list of dependency types. Empty list if there are no dependencies.
        """
        if not inspect.isclass(obj):
            return None

        init_signature = inspect.signature(obj.__init__)
        parameters = list(init_signature.parameters.values())

        # If only `self` exists, return no dependencies
        if len(parameters) == 1 and parameters[0].name == "self":
            return []

        dependencies = []
        for param in parameters:
            if param.name == "self":
                continue
            if param.annotation == param.empty:
                raise TypeError(
                    f"Dependency for parameter '{param.name}' in {obj.__name__} is not type-annotated."
                )
            dependencies.append(param.annotation)

        return dependencies

    def sort_dependencies(self, items: list[Any]) -> list[Any]:
        """
        Sorts the provided list of items based on their dependencies
        extracted from their __init__ signatures using topological sort.

        Args:
            items (list[Any]): A list of classes or objects to be sorted.

        Returns:
            list[Any]: The sorted list of items.
        """
        # Build dependency graph
        graph = {}

        for cls in items:
            try:
                graph[cls] = []
            except:
                continue

        independent_classes = []

        for cls in items:
            dependencies = self.get_dependencies(cls)

            if not dependencies:
                independent_classes.append(cls)
            else:
                for dependency in dependencies:
                    if dependency in items:  # Only include dependencies within the provided classes
                        graph[cls].append(dependency)

        # Perform topological sort
        visited = set()
        stack = independent_classes[:]  # Start with independent classes

        def visit(node):
            if node not in visited:
                visited.add(node)
                for neighbor in graph[node]:
                    visit(neighbor)
                if node in stack:
                    stack.remove(node)
                stack.append(node)

        for node in graph:
            if node not in visited:
                visit(node)

        return stack  # Reverse stack to get the correct order
    
    def inject(self, obj: type[T] | T | AbstractModule | AbstractFactory):
        """
        Resolves dependencies for a class or callable.

        Args:
            obj (type[T]): The class or callable to inject dependencies into.

        Returns:
            dict: A dictionary of resolved dependencies.
        """
        obj_args = {}

        if inspect.isfunction(obj) or inspect.ismethod(obj):
            obj_args = inspect.signature(obj).parameters

        else:
            obj_args = obj.__class__.__annotations__

        args = {}
        for name, abstract in obj_args.items():
            # abstract: inspect.Parameter = abstract
            if isinstance(abstract, inspect.Parameter):
                abstract = abstract.annotation

            injection = self.handle_di(abstract)
            if injection is not None:
                args[name] = injection

        return args
    
    def handle_di(self, interface: type[T]):
        """
        Resolves a dependency by checking the global and local service registry.

        Args:
            interface (type[T]): The class or interface to resolve.

        Returns:
            T: The resolved service instance.
        """
        service_registry = ServiceRegistry()

        global_import_object = service_registry.get_singletone(interface)
        local_import_object = self._module_scope.get(interface, None)

        if global_import_object:
            return global_import_object

        return local_import_object