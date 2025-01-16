from app_module import AppModule
from ascender.core._builder.build import build
from ascender.core.applications.create_application import createApplication
from bootstrap import appBootstrap

app = createApplication(config=appBootstrap)


if __name__ == "__main__":
    app.launch()