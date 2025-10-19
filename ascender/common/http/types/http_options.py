from typing import NotRequired, TypedDict
from httpx._types import QueryParamTypes, HeaderTypes, CookieTypes, AuthTypes, ProxyTypes, TimeoutTypes
from ssl import SSLContext


class HTTPOptions(TypedDict):
    params: NotRequired[QueryParamTypes]
    headers: NotRequired[HeaderTypes]
    cookies: NotRequired[CookieTypes]
    auth: NotRequired[AuthTypes]
    follow_redirects: NotRequired[bool]
    timeout: NotRequired[TimeoutTypes]