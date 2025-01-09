from __future__ import annotations
from typing import TYPE_CHECKING
from ascender.common import Injectable
from ascender.core.services import Service

if TYPE_CHECKING:
    from .circular_a_service import CircularAService


@Injectable()
class CircularBService(Service):
    def __init__(self, a: CircularAService):
        self.a = a