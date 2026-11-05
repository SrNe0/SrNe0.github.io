"""
Application configuration and constants.

This module contains all configuration values and constants used throughout
the Contact Manager application.
"""

from pathlib import Path

MENU_WIDTH = 50
MENU_MIN_OPTION = 1
MENU_MAX_OPTION = 7
EXIT_OPTION = 7

NOT_PROVIDED = "Not provided"
CLEAR_FIELD_VALUE = "-"

CONFIRM_YES_VALUES = {"yes", "y"}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JSON_FILE_PATH = PROJECT_ROOT / "contacts.json"
CSV_EXPORT_PATH = PROJECT_ROOT / "contacts_export.csv"
