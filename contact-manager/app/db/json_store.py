"""
JSON persistence layer.

This module handles loading and saving contacts to a JSON file. Saves are
atomic and damaged files are preserved as backups, so stored contacts are never
overwritten by accident. No business logic or console output is included here.
"""

import contextlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.configs.settings import JSON_FILE_PATH
from app.models.contact import Contact, normalize_contacts


def _backup_file(path: Path) -> Path:
    """
    Moves a damaged data file aside so it cannot be overwritten.

    Args:
        path: Path of the damaged file.

    Returns:
        The path of the backup file.

    Raises:
        OSError: If the file cannot be moved.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(f"{path.name}.corrupt-{timestamp}")
    os.replace(path, backup_path)
    return backup_path


def load_contacts(
    path: Path = JSON_FILE_PATH,
) -> tuple[list[Contact], Optional[str]]:
    """
    Loads contacts from the JSON file.

    A damaged file is moved to a backup before continuing. If only some records
    are damaged, the rest are recovered and saved.

    Args:
        path: Path of the JSON file.

    Returns:
        A tuple with the contacts and a warning for the user, or None if the
        file loaded without problems.

    Raises:
        OSError: If the file cannot be read, backed up, or repaired. Callers
            must not continue, since a later save could replace unread data.
    """
    if not path.exists():
        return [], None

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except ValueError:
        data = None

    if not isinstance(data, list):
        backup_path = _backup_file(path)
        return [], (
            f"{path.name} is damaged and was not loaded. "
            f"It was kept as {backup_path.name}. Starting with an empty list."
        )

    contacts, dropped = normalize_contacts(data)
    if not dropped:
        return contacts, None

    backup_path = _backup_file(path)
    save_contacts(contacts, path)
    return contacts, (
        f"{dropped} damaged record(s) in {path.name} could not be recovered. "
        f"The original file was kept as {backup_path.name}."
    )


def save_contacts(contacts: list[Contact], path: Path = JSON_FILE_PATH) -> None:
    """
    Saves contacts to the JSON file atomically.

    The data is written to a temporary file that replaces the original only
    after it is complete, so a failed save leaves the original file intact.

    Args:
        contacts: Contacts to save.
        path: Path of the JSON file.

    Raises:
        OSError: If the file cannot be written.
    """
    payload = json.dumps(contacts, indent=4, ensure_ascii=False)

    file_descriptor, temp_path = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as file:
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temp_path)
        raise
