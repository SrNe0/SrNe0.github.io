"""
User interface and menu functions.

This module handles basic user interaction: displaying menus, prompting for
input, and reading user responses.
"""

from typing import Callable

from app.configs.settings import (
    CLEAR_FIELD_VALUE,
    CONFIRM_YES_VALUES,
    MENU_MAX_OPTION,
    MENU_MIN_OPTION,
    MENU_WIDTH,
)
from app.utils.validators import parse_contact_id


def show_menu() -> None:
    """
    Displays the main menu.
    """
    print("\n" + "=" * MENU_WIDTH)
    print("CONTACT MANAGER".center(MENU_WIDTH))
    print("=" * MENU_WIDTH)
    print("1. Add contact")
    print("2. View all contacts")
    print("3. Search contacts")
    print("4. Update contact")
    print("5. Delete contact")
    print("6. Export to CSV")
    print("7. Exit")
    print("=" * MENU_WIDTH)


def prompt_menu_option() -> str:
    """
    Prompts the user to select a menu option.

    Returns:
        The user's menu selection as a string.
    """
    return input(f"\nSelect option ({MENU_MIN_OPTION}-{MENU_MAX_OPTION}): ").strip()


def prompt_string(message: str) -> str:
    """
    Prompts the user for a string input.

    Args:
        message: Prompt message displayed to the user.

    Returns:
        The user's input, stripped of leading/trailing whitespace.
    """
    return input(message).strip()


def prompt_contact_id(message: str) -> int:
    """
    Prompts the user for a contact ID until a valid one is provided.

    Args:
        message: Prompt message displayed to the user.

    Returns:
        The validated contact ID.
    """
    while True:
        contact_id = parse_contact_id(input(message).strip())
        if contact_id is not None:
            return contact_id
        print("Error: Please enter a positive whole number.")


def prompt_optional_field(
    message: str,
    is_valid: Callable[[str], bool],
    error_message: str,
    allow_clear: bool = False,
) -> str:
    """
    Prompts for an optional field until the value is valid or empty.

    Args:
        message: Prompt message displayed to the user.
        is_valid: Function that validates a non-empty value.
        error_message: Error displayed when the value is invalid.
        allow_clear: If True, CLEAR_FIELD_VALUE is also accepted.

    Returns:
        The validated value, an empty string, or CLEAR_FIELD_VALUE if allowed.
    """
    while True:
        value = input(message).strip()
        if not value or is_valid(value):
            return value
        if allow_clear and value == CLEAR_FIELD_VALUE:
            return value
        print_error(error_message)


def prompt_confirmation(message: str) -> bool:
    """
    Prompts the user for a yes/no confirmation.

    Args:
        message: Confirmation message displayed to the user.

    Returns:
        True if the user answered with an accepted "yes" value.
    """
    return input(message).lower().strip() in CONFIRM_YES_VALUES


def wait_for_enter() -> None:
    """
    Waits for the user to press Enter before continuing.
    """
    input("\nPress Enter to continue...")


def print_message(message: str) -> None:
    """
    Prints a message to the console.

    Args:
        message: The message to print.
    """
    print(message)


def print_error(message: str) -> None:
    """
    Prints an error message to the console.

    Args:
        message: The error message to print.
    """
    print(f"Error: {message}")
