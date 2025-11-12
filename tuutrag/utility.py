# ================================================================
# path: tuutrag/utility.py
# brief: utility helper functions and classes
# ================================================================

import sys

from typing import Any
from pathlib import Path
from loguru import logger
from configparser import ConfigParser


class Config():
    def __init__(self, path: str):
        self.path = Path(path)
        self.config = self._setup()

    def _setup(self) -> Any:
        config = ConfigParser()
        config.read(filenames=self.path, encoding='utf-8')

        return config

    # sect: section as '[SECTION]' | key: key as some_key = value
    def get(self, sect: str, key: str, **kwargs) -> Any:
        try:
            if kwargs.get('asint'):
                return self.config.getint(sect, key)
            return self.config.get(sect, key)
        except Exception:
            logger.debug(f"Error on {sect}-{key}")

    def __str__(self) -> str:
        return self.path.read_text(encoding='utf-8')


def get_base_path() -> Path:
    """Returns base (root) path ~/"""

    project_root = Path().resolve().parent
    sys.path.append(str(project_root))

    return project_root
