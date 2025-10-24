from ascender.core import AscModule
from tests.di.utils.examples.example_service import ExampleService
from tests.modules.example.first_module import FirstModule


@AscModule(
    imports=[
        FirstModule
    ],  # Should import nothing, because FirstModule didn't exported anything
    declarations=[],
    providers=[ExampleService],
    exports=[ExampleService],
)
class SecondModule: ...
