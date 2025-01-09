from typing import Annotated
from ascender.common import Injectable
from ascender.core.di.inject import Inject
from ascender.core.services import Service
from tests.di.examples.did_service import DidService


@Injectable()
class SampleService(Service):
    def __init__(self, did_service: DidService, some_settings: Annotated[str, Inject("settings")]):
        self.did_service = did_service
        self.some_settings = some_settings