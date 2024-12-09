from ascender.clis.new.new_module import NewModule
from ascender.clis.generator.generator_module import GeneratorModule
from ascender.clis.serve.serve_module import ServeModule
from ascender.common.module import AscModule


@AscModule(
    imports=[
        GeneratorModule,
        NewModule,
        ServeModule,
    ],
    declarations=[
    ],
    providers=[
    ],
    exports=[]
)
class CliModule:
    ...