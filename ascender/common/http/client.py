import asyncio
import json
from contextlib import _AsyncGeneratorContextManager
from typing import Any, Literal, TypeVar, cast, overload
from httpx import AsyncClient, Response
from pydantic import BaseModel
from reactivex import create, Observer, abc, Observable

from ascender.common.http.types.formdata import FormData

from ._transport import AscHTTPTransport
from .types.http_options import HTTPOptions

T = TypeVar("T")


class HTTPClient:
    def __init__(
        self,
        base_url: str,
        transport: AscHTTPTransport,
        **client_configs
    ):
        self.client = AsyncClient(
            base_url=base_url,
            transport=transport,
            **client_configs
        )

    async def get(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        options: HTTPOptions | None = None
    ) -> T:
        """Send a GET request to a desired endpoint.

        Args:
            _resp (type[T] | T, optional): The expected response type. Defaults to dict.
            url (str): The URL to send the request to.
            options (HTTPOptions | None, optional): Additional options for the request. Defaults to None.

        Returns:
            T: The response from the server.

        Raises:
            httpx.HTTPStatusError: If an error occurs during the HTTP request.
        """
        payload_options = {} if not options else options
        response = await self.client.get(url, **cast(HTTPOptions, payload_options))

        return cast(T, self.__handle_response(_resp, response=response))

    async def post(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        content: Any | BaseModel | FormData | None,
        options: HTTPOptions | None = None
    ) -> T:
        """Send a POST request to a desired endpoint.

        Args:
            _resp (type[T] | T, optional): The expected response type. Defaults to dict.
            url (str): The URL to send the request to.
            content (Any | BaseModel | None): The content to include in the request body (supports pydantic models).
            options (HTTPOptions | None, optional): Additional options for the request. Defaults to None.

        Returns:
            T: The response from the server.

        Raises:
            httpx.HTTPStatusError: If an error occurs during the HTTP request.
        """
        payload_options = {} if not options else options
        request_payload = self.__prepare_request_body(content)

        response = await self.client.post(url, **request_payload, **cast(HTTPOptions, payload_options) )# type: ignore

        return cast(T, self.__handle_response(_resp, response=response))

    async def put(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        content: Any | BaseModel | FormData | None,
        options: HTTPOptions | None = None
    ) -> T:
        """Send a PUT request to a desired endpoint.

        Args:
            _resp (type[T] | T, optional): The expected response type. Defaults to dict.
            url (str): The URL to send the request to.
            content (Any | BaseModel | None): The content to include in the request body (supports pydantic models).
            options (HTTPOptions | None, optional): Additional options for the request. Defaults to None.

        Returns:
            T: The response from the server.

        Raises:
            httpx.HTTPStatusError: If an error occurs during the HTTP request.
        """
        payload_options = {} if not options else options
        request_payload = self.__prepare_request_body(content)

        response = await self.client.put(url, **request_payload, **cast(HTTPOptions, payload_options)) # type: ignore

        return cast(T, self.__handle_response(_resp, response=response))

    async def patch(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        content: Any | BaseModel | FormData | None,
        options: HTTPOptions | None = None
    ) -> T:
        """Send a PATCH request to a desired endpoint.

        Args:
            _resp (type[T] | T, optional): The expected response type. Defaults to dict.
            url (str): The URL to send the request to.
            content (Any | BaseModel | None): The content to include in the request body (supports pydantic models).
            options (HTTPOptions | None, optional): Additional options for the request. Defaults to None.

        Returns:
            T: The response from the server.

        Raises:
            httpx.HTTPStatusError: If an error occurs during the HTTP request.
        """
        payload_options = {} if not options else options
        request_payload = self.__prepare_request_body(content)

        response = await self.client.patch(url, **request_payload, **cast(HTTPOptions, payload_options)) # type: ignore

        return cast(T, self.__handle_response(_resp, response=response))

    async def delete(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        options: HTTPOptions | None = None
    ) -> T:
        """Send a DELETE request to a desired endpoint.

        Args:
            _resp (type[T] | T, optional): The expected response type. Defaults to dict.
            url (str): The URL to send the request to.
            options (HTTPOptions | None, optional): Additional options for the request. Defaults to None.

        Returns:
            T: The response from the server.

        Raises:
            httpx.HTTPStatusError: If an error occurs during the HTTP request.
        """
        
        
        payload_options = {} if not options else options
        response = await self.client.delete(url, **cast(HTTPOptions, payload_options))

        return cast(T, self.__handle_response(_resp, response=response))

    @overload
    def stream(
        self,
        _resp: type[T] | T = dict,
        *,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        content: Any | BaseModel | FormData | None = None,
        options: HTTPOptions | None = None,
        as_observable: Literal[True] = True,
    ) -> Observable[T]:
        ...

    @overload
    def stream(
        self,
        _resp: type[T] | T = dict,
        *,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        content: Any | BaseModel | FormData | None = None,
        options: HTTPOptions | None = None,
        as_observable: Literal[False],
    ) -> _AsyncGeneratorContextManager[Response]:
        ...

    def stream(
        self,
        _resp: type[T] | T = dict,
        *,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        content: Any | BaseModel | FormData | None = None,
        options: HTTPOptions | None = None,
        as_observable: bool = True,
    ) -> Observable[T] | _AsyncGeneratorContextManager[Response]:
        """Send a streaming request to a desired endpoint.

        Args:
            _resp (type[T] | T, optional): The expected response type. Defaults to dict.
            method (Literal["GET", "POST", "PUT", "DELETE", "PATCH"]): The HTTP method to use for the request.
            url (str): The URL to send the request to.
            content (Any | BaseModel | None, optional): The content to include in the request body (supports pydantic models). Defaults to None.
            options (HTTPOptions | None, optional): Additional options for the request. Defaults to None.
            as_observable (bool, optional): When True (default), returns an Observable; when False, returns an async context manager for manual streaming.

        Returns:
            Observable[T] | _AsyncGeneratorContextManager[Response]: Stream subscription helper or the raw streaming context manager.

        Raises:
            httpx.HTTPError: If an error occurs during the HTTP request.
        """
        payload_options = {} if not options else options
        request_payload = self.__prepare_request_body(content)

        response_ctx = self.client.stream(method, url, **request_payload, **cast(HTTPOptions, payload_options)) # type: ignore
        
        if not as_observable:
            return response_ctx

        return create(cast(abc.Subscription[T], self.__handle_streaming(_resp, response=response_ctx)))

    def __prepare_request_body(
        self,
        content: Any | BaseModel | None
    ):
        if not content:
            return {}

        if isinstance(content, BaseModel):
            return {"json": cast(BaseModel, content).model_dump(mode="json")}
        
        if isinstance(content, FormData):
            return content._construct()
        
        return {"json": content}

    def __handle_streaming(
        self,
        _resp: type[T] | T = dict,
        *,
        response: _AsyncGeneratorContextManager[Response]
    ):
        def observable_response(observer: Observer[T], _):
            async def handle_request():
                try:
                    async with response as item:
                        async for line in item.aiter_text():
                            parsed = self.__parse_stream_chunk(_resp, line)
                            observer.on_next(parsed)

                    observer.on_completed()
                except Exception as exc:
                    observer.on_error(exc)

            asyncio.create_task(handle_request())
        return observable_response

    def __parse_stream_chunk(self, _resp: type[T] | T, chunk: str) -> T:
        if isinstance(_resp, BaseModel):
            return cast(T, type(_resp).model_validate_json(chunk))

        if isinstance(_resp, type) and issubclass(_resp, BaseModel):
            return cast(T, cast(type[BaseModel], _resp).model_validate_json(chunk))

        try:
            data = json.loads(chunk)
        except Exception:
            return cast(T, chunk)

        if isinstance(_resp, type):
            try:
                return cast(T, _resp(data))  # type: ignore[arg-type]
            except Exception:
                return cast(T, data)

        return cast(T, data)

    def __handle_response(
        self,
        _resp: type[T] | T = dict,
        *,
        response: Response
    ):
        response.raise_for_status()

        if isinstance(_resp, (dict, str, int, float, list, bool)):
            if response.headers.get("Content-Type", "") == "application/json":
                return cast(T, response.json())
            else:
                return cast(T, response.text)

        if issubclass(cast(type[T], _resp), BaseModel):
            _outload = cast(BaseModel, _resp).model_validate(
                response.json())
            return _outload

        try:
            return response.json()

        except Exception as e:
            return cast(T, response.text)
