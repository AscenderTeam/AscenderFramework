from ascender.core.applications.configure_imports import configure_imports

configure_imports()

from src.main import app

if __name__ == "__main__":
    app.launch()
