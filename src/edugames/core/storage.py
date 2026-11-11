"""JSON files in the user data directory, written atomically."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from platformdirs import user_data_dir

from edugames import APP_NAME

SCHEMA_VERSION = 1


def default_data_dir() -> Path:
    """Where the profiles are kept on this system (for example ~/Library/Application Support)."""
    return Path(user_data_dir(APP_NAME, appauthor=False))


def load_json(path: Path) -> dict[str, Any] | None:
    """The saved data, or None if the file is missing or unreadable.

    An unreadable file is renamed to `<name>.corrupt` (kept for inspection) instead of crashing.
    """
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        data = None
    if not isinstance(data, dict) or data.get("version") != SCHEMA_VERSION:
        os.replace(path, path.with_name(path.name + ".corrupt"))
        return None
    return data


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Write `data` (plus the schema version) so that a crash never leaves a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({**data, "version": SCHEMA_VERSION}, indent=2, ensure_ascii=False)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(payload)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
