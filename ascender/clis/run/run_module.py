from ascender.clis.run.run_app import RunCLI
from ascender.common.module import AscModule


@AscModule(
    imports=[],
    declarations=[],
    providers=[
        RunCLI
    ],
    exports=[]
)
class RunModule:
    ...