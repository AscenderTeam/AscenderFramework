from typing import Any, TypedDict


class StructureMetadata(TypedDict):
    filename: str
    metadata: dict[str, Any]