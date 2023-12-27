from core.cli.application import ContextApplication
from core.cli.main import BaseCLI
from core.cli.models import ArgumentCMD, OptionCMD

class Serve(BaseCLI):
    host: str = ArgumentCMD(ctype=str, default="127.0.0.1", required=False)
    port: int = OptionCMD(ctype=int, default=8000, required=False)

    def callback(self, ctx: ContextApplication):
        return ctx.application.run_server(self.host, self.port)