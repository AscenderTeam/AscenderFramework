from fastapi import FastAPI


class DefineAPIDocs:
    def __init__(
        self,
        title: str = "Ascender Framework API",
        description: str = "",
        swagger_url: str = "/docs",
        redoc_url: str = "/redoc",
    ):
        self.title = title
        self.description = description
        self.swagger_url = swagger_url
        self.redoc_url = redoc_url
    
    def update_instance(self, app: FastAPI):
        app.docs_url = self.swagger_url
        app.redoc_url = self.redoc_url

        app.setup()

        app.title = self.title
        app.description = self.description

        return app