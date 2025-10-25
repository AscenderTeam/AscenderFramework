import ssl

from ascender.core.di.interface.provider import Provider

from ._transport import AscHTTPTransport
from .client import HTTPClient
from .types.interceptors import Interceptor, InterceptorFn
from httpx._types import CertTypes


def provideHTTPClient(
        base_url: str = "",
        interceptors: list[InterceptorFn | type[Interceptor]] = [],
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        trust_env: bool = True,
        client_instance: type[HTTPClient] = HTTPClient,
        **additional_configs
) -> Provider:
    """Provide a configured HTTPClient instance.

    Args:
        base_url (str, optional): The base URL for the HTTP client. Defaults to "".
        interceptors (list[InterceptorFn | type[Interceptor]], optional): A list of interceptor functions or
            classes to use with the HTTP client. Defaults to [].
        verify (ssl.SSLContext | str | bool, optional): Whether to verify SSL certificates. Defaults to True.
        cert (CertTypes | None, optional): The SSL certificate to use. Defaults to None.
        trust_env (bool, optional): Whether to trust the system's CA certificates. Defaults to True.
        client_instance (type[HTTPClient], optional): The HTTP client class to use. Defaults to `HTTPClient`.
        **additional_configs: Additional keyword arguments forwarded to the HTTP client constructor.

    Returns:
        Provider: A provider for the HTTP client instance.
    """
    
    client = client_instance(base_url, AscHTTPTransport(
        interceptors=interceptors,
        verify=verify,
        cert=cert,
        trust_env=trust_env
    ), **additional_configs)
    return {
        "use_factory": lambda: client,
        "provide": client_instance
    }
