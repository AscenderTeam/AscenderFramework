from typing import Any
from typing_extensions import TypedDict


class TortoiseConfig(TypedDict):
    connections: dict[str, str]
    apps: dict[str, dict[str, Any]]
    use_tz: bool
    timezone: str