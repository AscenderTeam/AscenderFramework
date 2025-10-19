from typing import Callable, ForwardRef, Iterable
from ..interface.provider import Provider


def is_factory_provider(provider: Provider) -> bool:
    if not isinstance(provider, dict):
        return False
    
    return bool(provider.get("use_factory", None))


def is_static_class_provider(provider: Provider) -> bool:
    if not isinstance(provider, dict):
        return False
    
    use_class_attr = bool(provider.get("use_class", None))
    if not use_class_attr:
        return bool(provider.get("provide", None)) and bool(provider.get("deps", None)) and not is_factory_provider(provider)
    
    return use_class_attr


def is_value_provider(provider: Provider) -> bool:
    if not isinstance(provider, dict):
        return False
    
    return bool(provider.get("value", None))


def is_type_provider(provider: Provider) -> bool:
    return not (
        is_factory_provider(provider) and
        is_static_class_provider(provider) and
        is_value_provider(provider)
    ) and isinstance(provider, (type, ForwardRef))


def for_each_provider(providers: Iterable, fn: Callable[[Provider], None]):
    for provider in providers:
        if isinstance(provider, list):
            for_each_provider(provider, fn)
            continue

        fn(provider)