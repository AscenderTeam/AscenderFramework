from ascender.clis.new.new_app import NewCLI
from ascender.clis.new.new_service import NewService
from ascender.common.module import AscModule


@AscModule(
    imports=[],
    declarations=[],
    providers=[
        NewCLI,
        NewService
    ],
    exports=[]
)
class NewModule:
    ...