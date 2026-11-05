"""
CSV export.

This module writes contacts to a CSV file that spreadsheet applications can
open. No business logic or console output is included here.
"""

import csv
from pathlib import Path

from app.configs.settings import CSV_EXPORT_PATH
from app.models.contact import Contact

CSV_FIELDS = ("id", "name", "phone", "email")
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _escape_formula(value: object) -> object:
    """
    Stops spreadsheet applications from running a text value as a formula.

    Args:
        value: Field value to export.

    Returns:
        The value, prefixed with an apostrophe if it is text that starts like
        a formula.
    """
    if isinstance(value, str) and value.startswith(FORMULA_PREFIXES):
        return f"'{value}"
    return value


def export_contacts_csv(
    contacts: list[Contact], path: Path = CSV_EXPORT_PATH
) -> Path:
    """
    Writes contacts to a CSV file, replacing any previous export.

    Args:
        contacts: Contacts to export.
        path: Path of the CSV file.

    Returns:
        The path of the exported file.

    Raises:
        OSError: If the file cannot be written.
    """
    with open(path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for contact in contacts:
            writer.writerow(
                {field: _escape_formula(contact[field]) for field in CSV_FIELDS}
            )
    return path
