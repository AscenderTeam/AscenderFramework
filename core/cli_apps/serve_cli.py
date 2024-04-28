import socket
from typing import Literal, Optional

import requests
from core._builder.manager import BuildManager
from core.cli.application import ContextApplication
from core.cli.main import BaseCLI
from core.cli.models import OptionCMD
from rich.table import Table
from rich.panel import Panel
from rich.style import Style

from settings import TORTOISE_ORM


class ServerControlCLI(BaseCLI):
    host: str = OptionCMD("-h", ctype=str, default="127.0.0.1", required=False)
    port: int = OptionCMD("-p", ctype=int, default=8000, required=False)

    def callback(self, ctx: ContextApplication):
        return ctx.application.run_server(self.host, self.port)


class BuildControlCLI(BaseCLI):
    host: str = OptionCMD("-h", ctype=str, default="0.0.0.0", required=False)
    port: int = OptionCMD("-p", ctype=int, default=8000, required=False)
    workers: Optional[int] = OptionCMD(
        "-w", ctype=int, default=1, required=False)
    loop: Literal["auto", "asyncio", "uvloop"] = OptionCMD(
        default="auto", required=False)
    http: Literal["auto", "h11", "httptools"] = OptionCMD(
        default="auto", required=False)
    ws: Literal["auto", "none", "websockets", "wsproto"] = OptionCMD(
        default="auto", required=False)
    ws_max_size: int = OptionCMD(default=16777216, ctype=int, required=False)
    ws_max_queue: int = OptionCMD(default=32, ctype=int, required=False)
    ws_ping_interval: float = OptionCMD(
        default=20.0, ctype=float, required=False)
    ws_per_message_deflate: bool = OptionCMD(
        ctype=bool, default=True, required=False)
    lifespan: Literal["auto", "on", "off"] = OptionCMD(
        default="auto", required=False)
    interface: Literal["auto", "asgi3", "asgi2", "wsgi"] = OptionCMD(
        default="auto", required=False)
    log_level: Literal["critical", "error",
                       "warning", "info", "debug", "trace"] = OptionCMD(default="error", required=False)
    forwarded_allow_ips: Optional[str] = OptionCMD(required=False)
    root_path: str = OptionCMD(default="", required=False)
    limit_concurrency: Optional[int] = OptionCMD(ctype=int, required=False)
    backlog: int = OptionCMD(default=2048, ctype=int, required=False)
    limit_max_requests: Optional[int] = OptionCMD(ctype=int, required=False)
    timeout_keep_alive: int = OptionCMD(default=5, ctype=int, required=False)
    timeout_graceful_shutdown: Optional[int] = OptionCMD(
        ctype=int, required=False)
    ssl_keyfile: Optional[str] = OptionCMD(required=False)
    ssl_certfile: Optional[str] = OptionCMD(required=False)
    ssl_keyfile_password: Optional[str] = OptionCMD(required=False)
    ssl_version: int = OptionCMD(default=17, ctype=int, required=False)
    ssl_cert_reqs: int = OptionCMD(default=0, ctype=int, required=False)
    ssl_ca_certs: Optional[str] = OptionCMD(required=False)
    ssl_ciphers: str = OptionCMD(default="TLSv1", required=False)
    y: bool = OptionCMD("-y", ctype=bool, default=False, required=False)

    def callback(self, ctx: ContextApplication):
        ctx.console_print("""
[bold red]Ascender Framework CLI[/bold red]
[bold red]------------------------[/bold red][cyan]
   ___   _________  _______   ____
  / _ | / __/ ___/ / ___/ /  /  _/
 / __ |_\ \/ /__  / /__/ /___/ /
/_/ |_/___/\___/  \___/____/___/  [/cyan]

[bold red]------------------------[/bold red]
""")
        ctx.console_print(
            "[bold cyan]Building Asceder Framework application...[/bold cyan]")

        database_connections = TORTOISE_ORM["connections"]
        database_apps = TORTOISE_ORM["apps"]
        ctx.console_print(
            f"[green]Using {len(database_connections)} database connection(s)...[/green]")
        ctx.console_print(
            f"[green]Using {len(database_apps)} database app(s)...")

        for key, value in database_apps.items():
            ctx.console_print(
                "[cyan]Tortoise application [bold]{app_name}[/bold] included into loading[/cyan]".format(app_name=key))
            ctx.console_print("[bold yellow]These database entities will be loaded for app [cyan]{app_name}[/cyan]:[/bold yellow] [green]{models}[/]".format(
                app_name=key, models="[cyan] | [/cyan]".join(value["models"])))

        _parameters = {
            "host": self.host,
            "port": self.port,
            "workers": self.workers,
            "loop": self.loop,
            "http": self.http,
            "ws": self.ws,
            "ws_max_size": self.ws_max_size,
            "ws_max_queue": self.ws_max_queue,
            "ws_ping_interval": self.ws_ping_interval,
            "ws_per_message_deflate": self.ws_per_message_deflate,
            "lifespan": self.lifespan,
            "interface": self.interface,
            "log_level": self.log_level,
            "forwarded_allow_ips": self.forwarded_allow_ips,
            "root_path": self.root_path,
            "limit_concurrency": self.limit_concurrency,
            "backlog": self.backlog,
            "limit_max_requests": self.limit_max_requests,
            "timeout_keep_alive": self.timeout_keep_alive,
            "timeout_graceful_shutdown": self.timeout_graceful_shutdown,
            "ssl_keyfile": self.ssl_keyfile,
            "ssl_certfile": self.ssl_certfile,
            "ssl_keyfile_password": self.ssl_keyfile_password,
            "ssl_version": self.ssl_version,
            "ssl_cert_reqs": self.ssl_cert_reqs,
            "ssl_ca_certs": self.ssl_ca_certs,
            "ssl_ciphers": self.ssl_ciphers,
        }
        # Initialize builder
        _builder = BuildManager(ctx.application, **_parameters)
        # Initialize data table for confirmation
        data_table = Table("Parameter", "Value", "CLI Argument",
                           title="Production Server Parameters", border_style=Style(color="red", encircle=True))
        for key, value in _parameters.items():
            if key == "workers":
                data_table.add_row(key, str(value), f"--workers -w")
                continue
            if key == "host":
                data_table.add_row(
                    f"[bold]{key}[/bold]", f"[bold]{value}[/bold]", f"--host -h")
                continue
            if key == "port":
                data_table.add_row(
                    f"[bold]{key}[/bold]", f"[bold]{value}[/bold]", f"--port -p")
                continue
            data_table.add_row(key, str(value), f"--{key.replace('_', '-')}")

        ctx.console_print(table=data_table)
        if not self.y:
            _confirm = ctx.console_confirm(
                "[bold warning]Are you sure with these parameters?[/bold warning]")

            if _confirm:
                self.build_server(ctx, _builder)
            
            return
        
        self.build_server(ctx, _builder)

    def build_server(self, ctx: ContextApplication, _builder: BuildManager):
        ctx.console_print(
            "[bold green]Running a production server...[bold green]")
        ctx.console.log("Listening to {host}:{port}".format(
            host=self.host, port=self.port))

        try:
            connection_address = socket.gethostname()
            connection_address = socket.gethostbyname(connection_address)
        except:
            connection_address = self.host

        connection_panel = Panel("""
Local address: [cyan]http://{host}:{port}[/cyan]
Network address: [cyan]http://{public_host}:{port}[/cyan]
            """.format(host=self.host, port=self.port, public_host=connection_address), title="Connection Information", border_style=Style(color="cyan"))
        ctx.console_print(panel=connection_panel)
        _builder.classic_build()
