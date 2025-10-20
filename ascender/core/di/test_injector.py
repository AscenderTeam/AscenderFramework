from typing import Any, MutableSequence, Sequence, cast
from ascender.core.di.injector import AscenderInjector, T
from ascender.core.di.interface.consts import RAISE_NOT_FOUND
from ascender.core.di.interface.injector import InjectorOptions
from ascender.core.di.interface.provider import Provider
from ascender.core.di.interface.record import ProviderRecord
from ascender.core.di.overrider import InjectionOverriderContext, StaticOverrider
from ascender.core.di.utils.providers import for_each_provider, is_type_provider


class TestInjector(AscenderInjector):
    """
    A test injector that extends the AscenderInjector for testing purposes.
    
    This injector is used to provide a controlled environment for testing dependency injection
    without affecting the global state of the application.
    
    Test injectors are typically extend functionality of the base injector to allow for
    specific configurations or behaviors that are only relevant during testing.
    
    For example:
    - Dependency overriding for testing purposes.
    - Mocking or stubbing dependencies.
    
    It will be used only in test cases and only if ascender framework is being used in test mode.
    It inherits from `AscenderInjector` and sets the `_test_mode` attribute to `True` to indicate that it is in test mode.
    """
    _test_mode: bool

    _overrode: MutableSequence[type[Any] | str]
    
    def __init__(
        self,
        providers: Sequence[Provider],
        parent: AscenderInjector | None = None
    ):
        super().__init__(providers, parent)
        self._test_mode = True  # Indicates that this injector is in test mode
        self._overrode = []
        
        self.dependencies[TestInjector].add(ProviderRecord(self))
    
    def mock(self, providers: Sequence[Provider] | None = None) -> InjectionOverriderContext:
        """
        Initiate overide mock, it allows to configure the test injector.
        Override for instance, to provide a mock or stub for a specific provider.
        
        This method allows for dynamic overriding of providers in the test injector,
        which is useful for testing different configurations or behaviors.
        
        Parameters
        ----------
        providers : Sequence[Provider]
            List of providers to override the current ones.
        """
        return InjectionOverriderContext(cast(list | None, providers))
    
    def _get_overrode_deps(self):
        providers = StaticOverrider.overrides.get()
        
        if providers is not None:
            for_each_provider([providers], self.__reprocess_provider)
    
        """:internal:"""
    def __reprocess_provider(self, provider: Provider):
        """
        Processes each single provider and adds record to `dependencies`
        """
        # Resolves token of the provider
        provider_token = provider if isinstance(provider, type) else provider.get("provide")

        # Generate provider record
        provider_record = self.__provide_to_record(provider)

        if not is_type_provider(provider) and provider.get("multi", False):
            if provider_token not in self._overrode:
                self.dependencies[provider_token].clear()
            
            # Add to dependencies
            self.dependencies[provider_token].add(provider_record)
        else:
            self.dependencies[provider_token] = set([provider_record])

        if provider_token not in self._overrode:
            # Add to overrode list
            self._overrode.append(provider_token)
        
    def get(self, token: type[T] | str | Any, not_found_value: Any | None = ..., options: InjectorOptions = {"optional": False}) -> T | Any | None:
        # Ensure that we have the latest overrides before getting the token
        self._get_overrode_deps()
        
        # Call the parent method to get the token
        return super().get(token, not_found_value, options)
    
    def get_factory_def(self, token: type[Any] | str, self_only: bool = False, skip_self: bool = False):
        # Ensure that we have the latest overrides before getting the factory definition
        self._get_overrode_deps()
        
        # Call the parent method to get the factory definition
        return super().get_factory_def(token, self_only, skip_self)