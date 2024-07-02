"""
This file is used to configure the ORM settings & API Configurations.
Please do not store sensitive information in this file, this file is not for storing tokens and secret keys.
"""
import os

from fastapi.security import HTTPBearer

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": "database.db"  # Replace with your SQLite database file path
            }
        }
    },
    "apps": {
        "models": {
            "models": ["entities.test", "aerich.models"],  # Replace with the path to your models module
            "default_connection": "default"
        }
    }
}
DATABASE_CONNECTION = {
    "type": "dbstring",
    "content": "sqlite+aiosqlite:///database.db"
}
ORIGINS = [
    "*",
]

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
HEADERS = None
PLUGINS_LOGLEVEL = "INFO"
AUTHORIZATION_SCHEME = HTTPBearer()