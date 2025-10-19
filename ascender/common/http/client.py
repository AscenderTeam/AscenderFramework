from contextlib import _GeneratorContextManager
from threading import Thread
from typing import Any, Literal, TypeVar, cast
from httpx import AsyncClient, Response, stream
from pydantic import BaseModel
from reactivex import create, Observer, abc, Observable

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
        payload_options = {} if not options else options
        response = await self.client.get(url, **cast(HTTPOptions, payload_options))

        return cast(T, self.__handle_response(_resp, response=response))

    async def post(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        content: Any | BaseModel | None,
        options: HTTPOptions | None = None
    ) -> T:
        payload_options = {} if not options else options
        request_payload = self.__prepare_request_body(content)

        response = await self.client.post(url, **request_payload, **cast(HTTPOptions, payload_options) )# type: ignore

        return cast(T, self.__handle_response(_resp, response=response))

    async def put(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        content: Any | BaseModel | None,
        options: HTTPOptions | None = None
    ) -> T:
        payload_options = {} if not options else options
        request_payload = self.__prepare_request_body(content)

        response = await self.client.put(url, **request_payload, **cast(HTTPOptions, payload_options)) # type: ignore

        return cast(T, self.__handle_response(_resp, response=response))

    async def patch(
        self,
        _resp: type[T] | T = dict,
        *,
        url: str,
        content: Any | BaseModel | None,
        options: HTTPOptions | None = None
    ) -> T:
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
        payload_options = {} if not options else options
        response = await self.client.delete(url, **cast(HTTPOptions, payload_options))

        return cast(T, self.__handle_response(_resp, response=response))

    def stream(
        self,
        _resp: type[T] | T = dict,
        *,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        url: str,
        content: Any | BaseModel | None = None,
        options: HTTPOptions | None = None
    ) -> Observable[T]:
        payload_options = {} if not options else options
        request_payload = self.__prepare_request_body(content)

        resposne = stream(method, url, **request_payload, **cast(HTTPOptions, payload_options)) # type: ignore
        
        return create(cast(abc.Subscription[T], self.__handle_streaming(_resp, response=resposne)))

    def __prepare_request_body(
        self,
        content: Any | BaseModel | None
    ):
        if not content:
            return {}

        if isinstance(content, BaseModel):
            return {"json": cast(BaseModel, content).model_dump(mode="json")}

        return {"json": content}

    def __handle_streaming(
        self,
        _resp: type[T] | T = dict,
        *,
        response: _GeneratorContextManager[Response]
    ):
        def observable_response(observer: Observer[T], _):
            def handle_request():
                with response as item:
                    for line in item.iter_text():
                        observer.on_next(cast(T, line))
                    
                    observer.on_completed()

            Thread(target=handle_request).start()
        return observable_response

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
