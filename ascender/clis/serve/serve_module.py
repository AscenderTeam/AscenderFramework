from ascender.clis.serve.serve_service import ServeService
from ascender.clis.serve.serve_app import ServeCLI
from ascender.common.module import AscModule


@AscModule(
    imports=[],
    declarations=[],
    providers=[
        ServeCLI,
        ServeService
    ],
    exports=[]
)
class ServeModule:
    ...