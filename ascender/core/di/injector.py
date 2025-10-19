from __future__ import annotations

from collections import defaultdict
from inspect import isclass, isfunction, ismethod
from typing import Any, Callable, ForwardRef, Mapping, MutableMapping, MutableSequence, Sequence, Set, TypeVar, cast, overload

from ascender.core.di.abc.base_injector import Injector
from ascender.core.di.interface.consts import CIRCULAR, RAISE_NOT_FOUND, CyclicDependency
from ascender.core.di.interface.injector import InjectorOptions
from ascender.core.di.interface.record import ProviderRecord
from ascender.core.di.none_injector import NoneInjector
from ascender.core.di.utils.forward_ref import is_forward_ref, resolve_dep_forward_ref
from ascender.core.di.utils.injection_def import injection_def
from ascender.core.di.utils.providers import for_each_provider, is_factory_provider, is_static_class_provider, is_type_provider, is_value_provider

from .interface.provider import FactoryProvider, Provider, StaticClassProvider


T = TypeVar("T")


class AscenderInjector(Injector):
    """
    Ascender Injector is a runtime dependency injector for handling most of Ascender Framework's DI tasks starting from root to modules
    """
    dependencies: MutableMapping[type[Any] | str, Set[ProviderRecord[Any]]]
    
    # None injector exception if not found
    NONE_INJECTOR = NoneInjector()

    def __init__(
        self, 
        providers: Sequence[Provider],
        parent: AscenderInjector | None = None
    ):
        self.dependencies = defaultdict(set)
        
        self.providers = providers
        self.__parent = parent

        # Make sure to add this injector into injectable records
        self.dependencies[Injector] = set([ProviderRecord(self)])

        # Handle all specified providers now
        for_each_provider(self.providers, lambda p: self.__process_provider(p))

    def get(
        self,
        token: type[T] | str | Any,
        not_found_value: Any | None = RAISE_NOT_FOUND,
        options: InjectorOptions = {
            "optional": False
        }
    ) -> T | Any | None:
        return self.supply(
            token, 
            not_found_value=not_found_value,
            options=options
        )
    
    """:internal:"""
    def __process_provider(self, provider: Provider):
        """
        Processes each single provider and adds record to `dependencies`
        """
        # Resolves token of the provider
        provider_token = provider if isinstance(provider, type) else provider.get("provide")

        # Generate provider record
        provider_record = self.__provide_to_record(provider)

        if not is_type_provider(provider) and provider.get("multi", False):
            self.dependencies[provider_token].add(provider_record)
        else:
            self.dependencies[provider_token] = set([provider_record])
        
    """:internal:"""
    def __provide_to_record(self, provider: Provider):
        """
        Processes Provider type object and returns `ProviderRecord` object
        """
        if is_value_provider(provider):
            return ProviderRecord[Any](provider.get("value"))
        
        factory = self.__provide_to_factory(provider)
        if not factory:
            raise TypeError("Provider is not found")
        
        multi = False
        if not is_type_provider(provider):
            multi = provider.get("multi", False)

        return ProviderRecord[Any](None, factory, multi)
    
    """:internal:"""
    def __provide_to_factory(self, provider: Provider):
        """
        Processes Provider and places it into factory function
        """
        factory: Callable[[], Any] | None = None

        if is_type_provider(provider):
            if isinstance(provider, ForwardRef):
                _resolved = resolve_dep_forward_ref(provider, [d for d in self.dependencies.keys() if isinstance(d, type)])
                return self.inject_factory_def(_resolved)
            
            return self.inject_factory_def(provider) # type: ignore
        
        if is_value_provider(provider):
            factory = lambda: provider.get("value")
        
        elif is_factory_provider(provider):
            factory_provider = cast(FactoryProvider, provider)
            factory = lambda: factory_provider["use_factory"](*self.__inject_args(tokens=factory_provider.get("deps", [])))

        elif is_static_class_provider(provider):
            static_class_provider = cast(StaticClassProvider, provider)
            class_ref = static_class_provider.get("use_class", static_class_provider["provide"])
            if not isinstance(class_ref, type):
                raise TypeError("Class provider has string as provider and lacks of `use_class` parameter")
            if static_class_provider.get("deps", None):
                factory = lambda: class_ref(self.__inject_args(static_class_provider["deps"]))
            else:
                factory = self.inject_factory_def(class_ref)
        
        return factory
    
    def get_factory_def(
        self, 
        token: type[Any] | str, 
        self_only: bool = False, 
        skip_self: bool = False
    ):
        # If there is option skip self is set
        if skip_self and self.__parent:
            return self.__parent.get_factory_def(token)
        
        _injectable_value = None

        _injectable_value = self.dependencies[token] # Returns set even if token was not found, it will return empty set if not found

        # print(self.dependencies.keys())

        # Convert the set to list for better getter manipulation
        _injectable_value = list(_injectable_value)

        # If set is empty
        if not _injectable_value:
            # If not option `self_only` True and there is parent for current injector
            if self.__parent and not self_only:
                # Invoks parent's factory definition
                return self.__parent.get_factory_def(token)
            
            return None
        
        if len(_injectable_value) > 1:
            return _injectable_value
            
        return _injectable_value[0]

    def inject_factory_def(self, reference: type[Any]):
        """
        Injects factory definition. 
        It defines the specified reference and instatiates it within factory method.

        Args:
            reference (type[Any]): Reference object, usually class
        """
        def factory_def():
            if isclass(reference):
                _deps = injection_def(reference.__init__)
                
                return reference(**self.__inject_kargs(_deps))
            
            # If object is function or callable
            _deps = injection_def(reference)
            return reference(**self.__inject_kargs(_deps))
        
        return factory_def

    """:internal:"""
    def supply(
        self, 
        token: type[Any] | str, 
        not_found_value: Any | None = RAISE_NOT_FOUND,
        options: InjectorOptions = {"optional": False}
    ) -> Any:
        """
        Supplies Injector output with required providers by `token`
        """
        _deps = self.get_factory_def(token, options.get("only_self", False), options.get("skip_self", False))

        if _deps is None:
            return self.NONE_INJECTOR.get(token, not_found_value, options)
        
        # handle multi providers
        if isinstance(_deps, list):
            updated_deps: list[ProviderRecord[Any]] = []
            for dep in _deps:
                if dep.value is CIRCULAR:
                    raise CyclicDependency(f"Circular dependency detected for token: {token}")
                
                if not dep.value:
                    dep.value = CIRCULAR

                    if dep.factory is not None:
                        dep.value = dep.factory()
                        updated_deps.append(dep)
                        continue
                
                updated_deps.append(dep)
            
            self.dependencies[token] = set(updated_deps)
            return [dep.value for dep in updated_deps]
        
        if _deps.value is CIRCULAR:
            raise CyclicDependency(f"Circular dependency detected for token: {token}")
        if not _deps.value:
            _deps.value = CIRCULAR
            
            if _deps.factory:
                _deps.value = _deps.factory()
                self.dependencies[token] = set([_deps])
                return _deps.value
        
        return _deps.value
    
    def __inject_args(self, tokens: Sequence[type[Any] | str]) -> Sequence[Any]:
        """
        Injects in list type of python's arguments
        Returns Immutable Sequence of values for injection

        Args:
            tokens (Sequence[type[Any] | str]): Array of tokens to process

        Returns:
            Sequence[Any]: Array of supplied dependencies
        """
        type_records = [d for d in self.dependencies.keys() if isinstance(d, type)]
        dependencies: MutableSequence[Any] = []

        for token in tokens:
            if is_forward_ref(token):
                try:
                    token = resolve_dep_forward_ref(cast(ForwardRef | str, token), type_records)
                except TypeError:
                    pass
            # Supplies injector and current def with injected providers
            dependencies.append(self.supply(token))

        return dependencies
    
    def __inject_kargs(self, tokens: Mapping[str, type[Any] | str]) -> Mapping[str, Any]:
        """
        Injects in Mapping type of python's keyword-arguments
        Returns Immutable Mapping of values for injection

        Args:
            tokens (Mapping[str, type[Any] | str]): Mapping of tokens name: token

        Returns:
            Mapping[str, Any]: Mapping of output value name: supplied-dependency
        """
        type_records = [d for d in self.dependencies.keys() if isinstance(d, type)]
        dependencies: MutableMapping = {}
        for name, token in tokens.items():
            if is_forward_ref(token):
                try:
                    token = resolve_dep_forward_ref(cast(ForwardRef | str, token), type_records)
                except TypeError:
                    pass
            
            dependencies[name] = self.supply(token)

        return dependencies