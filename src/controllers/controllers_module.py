from ascender.core import AscModule
from controllers.main_controller import MainController


@AscModule(
    imports=[
        # MainController
    ],
    declarations=[],
    providers=[],
    exports=[
        # MainController
    ]
)
class ControllersModule:
    ...