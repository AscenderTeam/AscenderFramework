from ascender.common import Injectable
from ascender.core.services import Service
from tests.di.examples.circular_b_service import CircularBService


@Injectable()
class CircularAService(Service):
    def __init__(self, b: CircularBService):
        self.b = b