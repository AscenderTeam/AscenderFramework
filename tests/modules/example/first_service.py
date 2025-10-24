from ascender.common import Injectable
from ascender.core.services import Service
from tests.di.utils.examples.example_service import ExampleService


@Injectable()
class FirstService(Service):
    def __init__(self, example_service: ExampleService):
        self.example_service = example_service
