# ================================================================
# path: tuutrag/database.py
# brief: define database configuration and helper functions
# ================================================================

import os

from loguru import logger
from dataclasses import dataclass
from sqlite_utils import Database
from typing import Any, Union

PathLike = Union[str, os.PathLike]


@logger.catch()
def db_setup(
    filename: PathLike,
    enable_wall: bool = False,
    recreate: bool = True
) -> "Database":

    if recreate:
        db = Database(filename_or_conn=filename, recreate=True)
        logger.debug(f"Database {filename} has been (re)created.")
    else:
        if not os.access(filename, os.R_OK | os.W_OK):
            logger.debug(f"Database {filename} is inaccessible.")
            raise PermissionError(f"Cannot access database file: {filename}")
        db = Database(filename)
        logger.debug(f"Database {filename} loaded.")

    if enable_wall:
        db.enable_wal()
        logger.debug(f"WAL enabled for {filename}.")

    return db


@dataclass
class TableSchema:
    """A simple container for a table name and its schema."""
    name: str
    columns: dict[str, Any]
    pk: Any
