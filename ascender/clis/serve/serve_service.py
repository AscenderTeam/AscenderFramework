import os
import socket
from fastapi import FastAPI
from ascender.common import Injectable
from ascender.core._config.asc_config import _AscenderConfig
from ascender.core.services import Service
from watchfiles import run_process

from rich import print as console_print
from rich.panel import Panel
from rich.style import Style


def get_network_address():
    try:
        # Use a dummy connection to detect the primary network interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        network_address = s.getsockname()[0]
        s.close()
        return network_address
    except:
        return "127.0.0.1"
    

@Injectable(provided_in="root")
class ServeService(Service):
    LOG_CONFIG_WITHOUT_DEFAULT = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
            },
        },
        "handlers": {
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": [], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }

    def __init__(self):
        ...

    def start_reloader(self, app: FastAPI, host: str, port: int):
        run_process(os.getcwd(), target=self.start_server,
                    args=(app, host, port))

    def start_server(self, app: FastAPI, host: str, port: int):
        import uvicorn
        self.runtime_info(host, port)
        # source_path = _AscenderConfig().config.paths.source
        # print(f"{source_path}.main:app")
        uvicorn.run(f"main:app", host=host, port=port, factory=True, log_config=self.LOG_CONFIG_WITHOUT_DEFAULT,
                    **self.server_configurations())

    def server_configurations(self):
        configs = _AscenderConfig().config
        server_configs = configs.server

        return {
            "access_log": server_configs.requestLogging,
            "reload": server_configs.reload,
            "timeout_keep_alive": server_configs.timeout,
            "workers": server_configs.workers,
            "log_level": configs.logging.level
        }

    def runtime_info(self, host: str, port: int):
        config = _AscenderConfig().config

        console_print("""
[bold red]Ascender Framework CLI[/bold red]
[bold red]------------------------[/bold red][cyan]
   ___   _________  _______   ____
  / _ | / __/ ___/ / ___/ /  /  _/
 / __ |_\ \/ /__  / /__/ /___/ /
/_/ |_/___/\___/  \___/____/___/  [/cyan]

[bold red]------------------------[/bold red]
""")
        console_print(
            f"[bold green]Building and running {config.environment.default} server...[bold green]")
        console_print("Listening to {host}:{port}".format(
            host=host, port=port))

        connection_address = get_network_address()

        connection_panel = Panel("""
Local address: [cyan]http://{host}:{port}[/cyan]
Network address: [cyan]http://{public_host}:{port}[/cyan]
            """.format(host=host, port=port, public_host=connection_address), title="Connection Information", border_style=Style(color="cyan"))
        console_print(connection_panel)
