import sqlite3
from pathlib import Path

from database.schema import SCHEMA


DB_PATH = Path("data/finsight.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    connection.executescript(SCHEMA)

    connection.commit()
    connection.close()