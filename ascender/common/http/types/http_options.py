from ssl import SSLContext
from typing import NotRequired, TypedDict

from httpx._types import (AuthTypes, CookieTypes, HeaderTypes, ProxyTypes,
                          QueryParamTypes, TimeoutTypes)


class HTTPOptions(TypedDict):
    params: NotRequired[QueryParamTypes]
    headers: NotRequired[HeaderTypes]
    cookies: NotRequired[CookieTypes]
    auth: NotRequired[AuthTypes]
    follow_redirects: NotRequired[bool]
    timeout: NotRequired[TimeoutTypes]
