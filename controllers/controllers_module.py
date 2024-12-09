from controllers.app.app_module import AppModule
from ascender.common.module import AscModule


@AscModule(
    imports=[
        AppModule,
    ],
    declarations=[
    ],
    providers=[
    ],
    exports=[]
)
class ControllersModule:
    ...