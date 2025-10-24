from ascender.core import AscModule
from tests.modules.example.second_module import SecondModule


@AscModule(
    imports=[
        SecondModule
    ],  # Should import nothing, because FirstModule didn't exported anything
    declarations=[],
    providers=[],
    exports=[],
)
class ThirdModule: ...
