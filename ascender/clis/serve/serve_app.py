import os
from ascender.clis.serve.serve_service import ServeService
from ascender.core.cli_engine import Parameter, BasicCLI, Command


@Command(name="serve", description="Serve the Ascender application.", aliases=["s"], help="Start the Ascender application server.")
class ServeCLI(BasicCLI):
    host: str = Parameter("127.0.0.1", names=["-H", "--host"])
    port: int = Parameter(8000, names=["-p", "--port"])

    def __init__(self, serve_service: ServeService):
        self.serve_service = serve_service

    def execute(self):
        print("Starting Ascender server...")
        if int(os.getenv("CLI_MODE", "0")):
            raise ValueError("You can't run server in a non-initialized project!")
        
        self.serve_service.start_server(host=self.host, port=self.port)