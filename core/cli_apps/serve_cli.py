from core.cli.application import ContextApplication
from core.cli.main import BaseCLI

class Serve(BaseCLI):
    host: str = "127.0.0.1"
    port: int = 8000

    def callback(self, ctx: ContextApplication):
        return ctx.application.run_server(self.host, self.port)