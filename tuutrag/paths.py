# ================================================================
# path: tuutrag/paths.py
# brief: defines shared constants for paths
# ================================================================
import os


# <define dir> BASE: Base directory path for /tuutrag-open
DIR_BASE: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# <define dir> PARENT: Parent directory paths in /tuutrag-open/*
DIR_TUUTRAG: str = os.path.join(DIR_BASE, "tuutrag")
DIR_DATA: str = os.path.join(DIR_BASE, "data")

# <define dir> PARENT/CHILD (data): Child directories for data path in /tuutrag/data/*
DIR_DATA_SCRAPED: str = os.path.join(DIR_DATA, "scraped")

# <define file> CONFIG: Configuration files
CONFIG_INI: str = os.path.join(DIR_BASE, "config.ini")

__all__: list[str] = [name for name in globals() if name.isupper()]