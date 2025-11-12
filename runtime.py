################################
# Run time script. Execute TUUT
################################

import os
from pathlib import Path
from loguru import logger
from typing import Union, Any
from sqlite_utils import Database
from sqlite_utils.db import Table
from tuutrag.utility import Config, get_base_path
from tuutrag.database import db_setup, TableSchema


# Paths used throughout the runtime process
DIR_BASE: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
DIR_TUUTRAG: str = os.path.join(DIR_BASE, "tuutrag")
DIR_DATA: str = os.path.join(DIR_BASE, "data")
DIR_SCRIPTS: str = os.path.join(DIR_BASE, "scripts")
DIR_DATA_CCSDS: str = os.path.join(DIR_DATA, "ccsds")
DIR_DATA_META: str = os.path.join(DIR_DATA, "meta")
DIR_DATA_REQUIREMENTS: str = os.path.join(DIR_DATA, "requirements")
DIR_DATA_DATABASES: str = os.path.join(DIR_DATA, "databases")
FILE_CONFIG_INI: str = os.path.join(DIR_BASE, "config.ini")
FILE_LOGGER: str = os.path.join(DIR_BASE, "logger.log")

logger.add(FILE_LOGGER)

doc_schema = TableSchema(
    name="Document",
    columns={
        "id": int,
        "hash": str,
        "file_name": str,
        "blob": str
    },
    pk="id"
)

project_root = get_base_path()

config = Config(FILE_CONFIG_INI)

sqlite_db: "Database" = db_setup(
    filename=Path(DIR_DATA_DATABASES) / config.get("SQLITE", "filename"),
    enable_wall=True,
    recreate=True
)

documents: Union["Table", Any] = sqlite_db[doc_schema.name]
documents.create(doc_schema.columns, pk=doc_schema.pk)
