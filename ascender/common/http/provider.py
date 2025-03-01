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
