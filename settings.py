"""
This file is used to configure the ORM settings & API Configurations.
Please do not store sensitive information in this file, this file is not for storing tokens and secret keys.
"""
import os
from core.extensions.authentication import AscenderAuthenticationFramework

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
            "models": [AscenderAuthenticationFramework.use_authentication_database(), "aerich.models"],  # Replace with the path to your models module
            "default_connection": "default"
        }
    }
}
ORIGINS = [
    "*",
]

BASE_PATH = os.path.dirname(os.path.abspath(__file__))