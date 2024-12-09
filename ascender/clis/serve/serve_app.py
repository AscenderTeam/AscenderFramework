import os
from ascender.clis.serve.serve_service import ServeService
from ascender.core.cli.application import ContextApplication
from ascender.core.cli import BaseCLI
from ascender.core.cli.models import OptionCMD


class ServeCLI(BaseCLI):
    host: str = OptionCMD("-h", ctype=str, default="127.0.0.1", required=False)
    port: int = OptionCMD("-p", ctype=int, default=8000, required=False)

    def __init__(self, serve_service: ServeService):
        self.serve_service = serve_service

    def callback(self, ctx: ContextApplication):
        if int(os.getenv("CLI_MODE", "0")):
            raise ValueError("You can't run server in a non-initialized project!")
        
        self.serve_service.start_server(ctx.application.app, host=self.host, port=self.port)