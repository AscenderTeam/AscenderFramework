"""
This file is used to configure the ORM settings & API Configurations.
Please do not store sensitive information in this file, this file is not for storing tokens and secret keys.
"""
import os


DATABASE_CONNECTION = {
    "type": "dbstring",
    "content": "sqlite+aiosqlite:///database.db",
    "entities": ["entities.user"],
}

ORIGINS = [
    "*",
]

BASE_PATH = os.path.dirname(os.path.abspath(__file__))