from typing import NotRequired, TypedDict
from ascender.common.microservices.types.transport import Transport


class MicroserviceOptions(TypedDict):
    token: str
    options: Transport
    with_client_proxy: NotRequired[bool]