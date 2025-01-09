from typing import TypeVar, cast
from ascender.core.di.interface.record import ProviderRecord
from ascender.core.di.utils.providers import is_factory_provider, is_static_class_provider, is_value_provider
from ..interface.provider import FactoryProvider, Provider, StaticClassProvider, ValueProvider


T = TypeVar("T")


def make_record(token: type[T], provider: Provider):
    
    if is_factory_provider(provider):
        factory_provider = cast(FactoryProvider, provider)
        return ProviderRecord[T](factory_provider["use_factory"](), factory_provider["use_factory"])
    
    if is_static_class_provider(provider):
        static_class_provider = cast(StaticClassProvider, provider)
        use_class = static_class_provider.get("use_class", static_class_provider["provide"])

        if not isinstance(use_class, type):
            raise ValueError("There is no class defined in Static Class Provider! Use `ValueProvider` instead!")
        
        return ProviderRecord[T](static_class_provider.get("use_class", use_class()),)
    
    if is_value_provider(provider):
        value_provider = cast(ValueProvider, provider)
        
        return ProviderRecord[T](value_provider["value"], None)