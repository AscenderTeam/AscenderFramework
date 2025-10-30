from contextvars import ContextVar, Token
from typing import Literal, Self

from ascender.core.di.interface.provider import Provider


class InjectionOverriderContext:
    def __init__(self, providers: list[Provider] | None = None) -> None:
        self.token: Token[Provider | None] | None = None
        self.providers = providers
    
    def __enter__(self) -> Self:
        self.token = StaticOverrider.override(self.providers)
        return self
    
    def override(self, providers: list[Provider] | None) -> None:
        """
        Override the current providers with the given list of providers.

        Parameters
        ----------
        providers : list[Provider] | None
            List of providers to override the current ones. If None, it will not change the current providers.
            NOTE: That tokens can match already existing providers, for testing purposes.
        """
        if providers is not None:
            if self.providers is not None:
                self.providers.extend(providers)
            else:
                self.providers = providers
        
        StaticOverrider.reset(self.token)
        self.token = StaticOverrider.override(self.providers)

    def __exit__(self, exc_type, exc_val, exc_tb) -> Literal[False]:
        StaticOverrider.reset(self.token)
        return False


class StaticOverrider:
    """
    A static overrider for the Ascender framework's Dependency Injection System.
    It allows for overriding the default behavior of the framework's injector and injection system.
    This is useful for testing or when you need to change the behavior of the DI system without
    modifying the framework's core code.
    """
    overrides: ContextVar[Provider | None] = ContextVar("overrides", default=None)
    
    @staticmethod
    def override(providers: Provider | None = None) -> Token[Provider | None]:
        """
        Override the default behavior of the Ascender framework.
        """
        return StaticOverrider.overrides.set(providers)
    
    @staticmethod
    def reset(token: Token[Provider | None] | None = None) -> None:
        """
        Reset the overrides to the default behavior of the Ascender framework.
        """
        StaticOverrider.overrides.reset(token) if token else StaticOverrider.overrides.set(None)