from fastapi import FastAPI

from ascender.core._config.asc_config import _AscenderConfig


class DefineAPIDocs:
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        swagger_url: str = "/docs",
        redoc_url: str = "/redoc",
    ):
        self.config = _AscenderConfig().config
        self.title = title if title else self.config.project.get("name", "Ascender Framework API")
        self.description = description if description else self.config.project.get("description", "An API project powered by Ascender Framework")
        self.swagger_url = swagger_url
        self.redoc_url = redoc_url
    
    def update_instance(self, app: FastAPI):
        app.docs_url = self.swagger_url
        app.redoc_url = self.redoc_url

        app.setup()

        app.title = self.title
        app.description = self.description

        return app