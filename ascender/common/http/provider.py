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
    """
    Provides an HTTPClient instance configured with AscHTTPTransport.

    Parameters
    ----------
    base_url : str, optional
        The base URL for the HTTP client, by default ""
    interceptors : list[InterceptorFn  |  type[Interceptor]], optional
        A list of interceptor functions or classes to use with the HTTP client, by default []
    verify : ssl.SSLContext | str | bool, optional
        Whether to verify SSL certificates, by default True
    cert : CertTypes | None, optional
        The SSL certificate to use, by default None
    trust_env : bool, optional
        Whether to trust the system's CA certificates, by default True
    client_instance : type[HTTPClient], optional
        The HTTP client class to use, by default HTTPClient

    Returns
    -------
    Provider
        A provider for the HTTP client instance.
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
