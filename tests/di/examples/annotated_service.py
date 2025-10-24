from typing import Annotated

from ascender.common import Injectable
from ascender.core.di.inject import Inject
from ascender.core.services import Service


@Injectable()
class AnnotatedService(Service):
    def __init__(self, some_settings: Annotated[str, Inject("settings")]):
        self.some_settings = some_settings
