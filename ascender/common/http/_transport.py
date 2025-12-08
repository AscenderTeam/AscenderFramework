from inspect import isclass
import ssl
from typing import Any, cast
from httpx import AsyncBaseTransport, Request, AsyncHTTPTransport, Response
from httpx._types import CertTypes, ProxyTypes
from httpx._config import Limits, DEFAULT_LIMITS

from ascender.core.applications.root_injector import RootInjector

from .types.interceptors import Interceptor, InterceptorFn


class AscHTTPTransport(AsyncBaseTransport):
    def __init__(
        self,
        interceptors: list[InterceptorFn | type[Interceptor]] = [],
        verify: ssl.SSLContext | str | bool = True,
        cert: CertTypes | None = None,
        trust_env: bool = True,
        http1: bool = True,
        http2: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        proxy: ProxyTypes | None = None,
        uds: str | None = None,
        local_address: str | None = None,
        retries: int = 0,
        socket_options: Any | None = None,
    ) -> None:
        super().__init__()
        self.interceptors = interceptors
        self.transport = AsyncHTTPTransport(verify=verify, cert=cert, trust_env=trust_env,
                                            http1=http1, http2=http2, limits=limits,
                                            proxy=proxy, uds=uds, local_address=local_address,
                                            retries=retries, socket_options=socket_options)

        self._fn_interceptors: list[InterceptorFn] = []

        self.load_interceptors()

    def load_interceptors(self):
        for interceptor in self.interceptors:
            if isclass(interceptor):
                if issubclass(cast(type[Interceptor], interceptor), Interceptor):
                    RootInjector.providers.append({
                        "provide": "HTTP_INTERCEPTOR",
                        "use_class": interceptor,
                        "multi": True
                    })
                    continue

                raise TypeError(
                    f"Only classes types that extend `Interceptor` are allowed for HTTP interceptors, but got {interceptor.__name__}")

            self._fn_interceptors.append(interceptor)

    async def handle_async_request(self, request: Request) -> Response:
        # Request modification
        modified_request = request
        # Handle class interceptors based on dependency injection
        class_interceptors: list[Interceptor] | Interceptor = RootInjector().get(
            "HTTP_INTERCEPTOR", not_found_value=[], options={"optional": True}) # type: ignore

        modified_request = await self.request_class_interceptors(modified_request, class_interceptors)

        # Handle function interceptors on they own
        for interceptor_fn in self._fn_interceptors:
            # type: ignore
            modified_request = await interceptor_fn(modified_request)

        response = await self.transport.handle_async_request(modified_request)

        # Intercept response and possibly modify it if needed
        response = await self.response_class_interceptors(response, class_interceptors)

        return response

    async def request_class_interceptors(self, request: Request, class_interceptors: list[Interceptor] | Interceptor):
        """Handle class interceptors and invoke their `handle_request` methods.

        Args:
            request (Request): The outgoing HTTP request to process.
            class_interceptors (list[Interceptor] | Interceptor): Interceptor instance(s) returned by the injector.

        Returns:
            Request: The potentially modified request after applicable interceptors have run.
        """

        # Usually, injector returns instance itself if there's only one multi value provider.
        if not isinstance(class_interceptors, list):
            if type(class_interceptors) in self.interceptors:
                request = await class_interceptors.handle_request(request)

        else:
            for interceptor in class_interceptors:
                if type(interceptor) not in self.interceptors:
                    continue

                request = await interceptor.handle_request(request)
        
        return request
    
    async def response_class_interceptors(self, response: Response, class_interceptors: list[Interceptor] | Interceptor):
        """Handle class interceptors and invoke their `handle_response` methods.

        Args:
            response (Response): The HTTP response to process.
            class_interceptors (list[Interceptor] | Interceptor): Interceptor instance(s) returned by the injector.

        Returns:
            Response: The potentially modified response after applicable interceptors have run.
        """

        # Usually, injector returns instance itself if there's only one multi value provider.
        if not isinstance(class_interceptors, list):
            if type(class_interceptors) in self.interceptors:
                response = await class_interceptors.handle_response(response)

        else:
            for interceptor in class_interceptors:
                if type(interceptor) not in self.interceptors:
                    continue

                response = await interceptor.handle_response(response)
        
        return response

    async def aclose(self) -> None:
        return await self.transport.aclose()
