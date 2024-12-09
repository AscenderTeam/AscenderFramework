from controllers.app.guards.auth_guard import AuthGuard
from controllers.app.guards.users_guard import UsersGuard
from controllers.app.app_repository import AppRepo
from ascender.common import ProvideRepository
from controllers.app.app_service import AppService
from controllers.app.app_controller import AppController
from ascender.common.module import AscModule


@AscModule(
    imports=[
    ],
    declarations=[
        UsersGuard,
        AuthGuard,
        AppController,
    ],
    providers=[
        ProvideRepository(AppRepo),
        AppService,
    ],
    exports=[]
)
class AppModule:
    ...