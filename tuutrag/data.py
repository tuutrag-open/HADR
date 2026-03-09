import os
from pathlib import Path


def _locate_data_root() -> Path:
    candidate = Path(os.getcwd()).parent / "data"
    if candidate.is_dir():
        return candidate
    raise FileNotFoundError(
        f"Could not locate 'data/' relative to notebook directory: {os.getcwd()}\n"
        "Ensure the notebook server was launched from the project root."
    )


class DataManager:

    _SEARCH_DIRS: tuple[str, ...] = (
        "raw",
        "interim",
        "processed",
        "api/batch_staging",
        "api/leaf_batches",
    )

    def __init__(self, root: Path | None = None) -> None:
        self._root: Path = root or _locate_data_root()

    # --- Directory shortcuts -------------------------------------------

    @property
    def root(self) -> Path:
        return self._root

    @property
    def raw(self) -> Path:
        return self._root / "raw"

    @property
    def interim(self) -> Path:
        return self._root / "interim"

    @property
    def processed(self) -> Path:
        return self._root / "processed"

    @property
    def api(self) -> Path:
        return self._root / "api"

    @property
    def batch_staging(self) -> Path:
        return self._root / "api" / "batch_staging"

    @property
    def leaf_batches(self) -> Path:
        return self._root / "api" / "leaf_batches"

    @property
    def qdrant(self) -> Path:
        return self._root / "api" / "qdrant"

    # --- File resolution -----------------------------------------------

    def find(self, filename: str) -> Path:
        """
        Find a file by name across immediate data directories.

        Parameters
        ----------
        filename : bare filename, e.g. "fixed_size_chunks.json"
        """
        matches = [
            self._root / d / filename
            for d in self._SEARCH_DIRS
            if (self._root / d / filename).is_file()
        ]

        if not matches:
            raise FileNotFoundError(f"'{filename}' not found in any data directory.")

        if len(matches) > 1:
            found = "\n  ".join(str(p) for p in matches)
            raise ValueError(
                f"'{filename}' found in multiple locations:\n  {found}\n"
                f"Use the directory property directly, e.g. D.processed / '{filename}'"
            )

        return matches[0]

    def glob(self, pattern: str) -> list[Path]:
        """Glob a pattern across all search directories."""
        return [
            p
            for d in self._SEARCH_DIRS
            for p in (self._root / d).glob(pattern)
        ]

    def __repr__(self) -> str:
        return f"DataManager(root={self._root})"

    def __truediv__(self, other: str) -> Path:
        return self._root / other


D = DataManager()