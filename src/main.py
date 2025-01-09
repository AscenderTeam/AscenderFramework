from app_module import AppModule
from ascender.core._builder.build import build
from ascender.core.applications.create_application import createApplication

app = createApplication(app_module=AppModule)


if __name__ == "__main__":
    app.launch()