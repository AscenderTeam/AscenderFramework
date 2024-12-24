from ascender.abstracts.middleware import AscenderMiddleware
from ascender.abstracts.module import AbstractModule
from ascender.common.injectfn import inject
from ascender.core.application import Application
from starlette.types import ASGIApp


class UseMiddlewares(AbstractModule):
    instances: list[AscenderMiddleware]
    
    def __init__(self, *middlewares: AscenderMiddleware):
        self.middlewares = middlewares
        self.instances = []
    
    def on_module_init(self):
        application = inject(Application)
        for middleware in self.middlewares:
            self.instances.append(middleware)
            application.app.add_middleware(self.middleware_factory(middleware))
    
    async def on_application_bootstrap(self, application):
        for middleware in self.instances:
            params = application.service_registry.get_parameters(middleware.__post_init__)
            middleware.__post_init__(**params)
    
    def middleware_factory(self, middleware: AscenderMiddleware):
        def middleware_wrapper(app: ASGIApp):
            middleware.app = app
            return middleware

        return middleware_wrapper