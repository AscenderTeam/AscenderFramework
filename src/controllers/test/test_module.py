from src.controllers.test.some_service import SomeService
from controllers.test.test_repository import TestRepo
from ascender.core.utils.repository import provideRepository
from controllers.test.test_service import TestService
from controllers.test.test_controller import TestController
from ascender.core import AscModule


@AscModule(
    imports=[
    ],
    declarations=[
        TestController,
    ],
    providers=[
        SomeService,
        TestService,
        provideRepository(TestRepo),
    ],
    exports=[
        TestController
    ]
)
class TestModule:
    ...