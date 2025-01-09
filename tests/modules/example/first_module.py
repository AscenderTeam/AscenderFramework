from ascender.core import AscModule
from tests.di.utils.examples.example_service import ExampleService
from tests.modules.example.first_service import FirstService


@AscModule(
    imports=[],
    declarations=[],
    providers=[
        ExampleService,
        FirstService
    ],
    exports=[]
)
class FirstModule:
    ...