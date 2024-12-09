from __future__ import annotations
import os
from typing import TYPE_CHECKING, Literal, Optional

import uvicorn

from settings import HEADERS

# TYPE CHECKING
if TYPE_CHECKING:
    from ascender.core.application import Application


class BuildManager:
    def __init__(self, app: Application, host: str, port: int, *,
                 workers: Optional[int] = None, loop: Literal["auto", "asyncio", "uvloop"] = "auto",
                 http: Literal["auto", "h11", "httptools"] = "auto", ws: Literal["auto", "none", "websockets", "wsproto"] = "auto",
                 ws_max_size: int = 16777216,
                 ws_max_queue: int = 32,
                 ws_ping_interval: float = 20.0,
                 ws_per_message_deflate: bool = True,
                 lifespan: Literal["auto", "on", "off"] = "auto",
                 interface: Literal["auto", "asgi3", "asgi2", "wsgi"] = "auto",
                 log_level: Literal["critical", "error",
                                    "warning", "info", "debug", "trace"] = "trace",
                 forwarded_allow_ips: Optional[str] = None,
                 root_path: Optional[str] = None,
                 limit_concurrency: Optional[int] = None,
                 backlog: Optional[int] = None,
                 limit_max_requests: Optional[int] = None, timeout_keep_alive: Optional[int] = None,
                 timeout_graceful_shutdown: Optional[int] = None,
                 ssl_keyfile: Optional[os.PathLike] = None,
                 ssl_certfile: Optional[os.PathLike] = None,
                 ssl_keyfile_password: Optional[str] = None,
                 ssl_version: int = 17,
                 ssl_cert_reqs: int = 0,
                 ssl_ca_certs: Optional[str] = None,
                 ssl_ciphers: str = "TLSv1") -> None:
        self.app = app

        self.server_host = host
        self.server_port = port
        self.server_settings = {
            "workers": workers,
            "loop": loop,
            "http": http,
            "ws": ws,
            "ws_max_size": ws_max_size,
            "ws_max_queue": ws_max_queue,
            "ws_ping_interval": ws_ping_interval,
            "ws_per_message_deflate": ws_per_message_deflate,
            "lifespan": lifespan,
            "interface": interface,
            "log_level": log_level,
            "forwarded_allow_ips": forwarded_allow_ips,
            "root_path": root_path,
            "limit_concurrency": limit_concurrency,
            "backlog": backlog,
            "limit_max_requests": limit_max_requests,
            "timeout_keep_alive": timeout_keep_alive,
            "timeout_graceful_shutdown": timeout_graceful_shutdown,
            "ssl_keyfile": ssl_keyfile,
            "ssl_certfile": ssl_certfile,
            "ssl_keyfile_password": ssl_keyfile_password,
            "ssl_version": ssl_version,
            "ssl_cert_reqs": ssl_cert_reqs,
            "ssl_ca_certs": ssl_ca_certs,
            "ssl_ciphers": ssl_ciphers,
            "headers": HEADERS
        }

    def classic_build(self):
        """
        ## Classic Build

        Classic build is only runs uvicorn in debug - off mode.
        Build also allows developer to run uvicorn server with custom parameters
        """
        if self.app._on_injections_run is not None:
            self.app._on_injections_run(self.app)
        self.app._on_server_start(self.app)
        uvicorn.run(self.app.app, host=self.server_host, port=self.server_port, **self.server_settings)