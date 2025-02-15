from typing import Literal, Sequence, TypedDict


class KafkaMetadata(TypedDict):
    transporter: Literal["kafka"]
    pattern: str
    partition: int
    offset: int
    key: bytes | None
    timestamp: int
    timestamp_type: int | None
    headers: Sequence[tuple[str, bytes]]