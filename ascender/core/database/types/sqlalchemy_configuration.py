from typing import Literal
from typing_extensions import TypedDict


class SQLAlchemyConfig(TypedDict):
    type: Literal["dbstring"]
    content: str
    entities: list[str]