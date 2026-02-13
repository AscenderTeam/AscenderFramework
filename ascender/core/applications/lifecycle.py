from ascender.core import Provider
from typing import Sequence


def provideLifecycle(tokens: Sequence[str | type]) -> Provider:
    return {
        "provide": "LIFECYCLE_TOKENS",
        "value": tokens,
        "multi": True
    }