from ascender.clis.generator.edit_generator_service import EditGeneratorService
from ascender.clis.generator.generator_app import GeneratorCLI
from ascender.clis.generator.create_generator_service import CreateGeneratorService
from ascender.common.module import AscModule


@AscModule(
    imports=[],
    declarations=[],
    providers=[
        CreateGeneratorService,
        EditGeneratorService,
        GeneratorCLI,
    ],
    exports=[
        GeneratorCLI
    ]
)
class GeneratorModule:
    ...