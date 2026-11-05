"""
Contact Manager (CLI) - Main Entry Point.

A local CRUD application that manages contacts with JSON persistence using
a layered architecture. This module intentionally avoids classes (OOP) and
uses functions only.

Features:
- Create: Add a contact
- Read: List contacts, search by ID, name, phone, or email
- Update: Edit or clear contact fields
- Delete: Remove a contact
- Export: Write contacts to a CSV file
- Persistence: Automatic JSON file storage
"""

import sys

from app.configs.settings import EXIT_OPTION, MENU_MAX_OPTION, MENU_MIN_OPTION
from app.db.json_store import load_contacts
from app.interface.contact_flows import (
    add_contact_flow,
    delete_contact_flow,
    export_contacts_flow,
    search_contacts_flow,
    update_contact_flow,
    view_all_contacts_flow,
)
from app.interface.menu import (
    print_error,
    print_message,
    prompt_menu_option,
    show_menu,
    wait_for_enter,
)
from app.models.contact import Contact
from app.utils.console import clear_screen

GOODBYE_MESSAGE = "\nThank you for using Contact Manager!"

MENU_ACTIONS = {
    "1": add_contact_flow,
    "2": view_all_contacts_flow,
    "3": search_contacts_flow,
    "4": update_contact_flow,
    "5": delete_contact_flow,
    "6": export_contacts_flow,
}


def run_menu_loop(contacts: list[Contact]) -> None:
    """
    Shows the menu and runs the selected actions until the user exits.

    Args:
        contacts: Contacts loaded at startup.
    """
    greeting = "\nWelcome to Contact Manager!"

    while True:
        clear_screen()
        print_message(greeting)
        greeting = ""
        show_menu()

        option = prompt_menu_option()

        if option == str(EXIT_OPTION):
            print_message(GOODBYE_MESSAGE)
            return

        action = MENU_ACTIONS.get(option)
        if action is None:
            print_message(
                "\nInvalid option. "
                f"Please select {MENU_MIN_OPTION}-{MENU_MAX_OPTION}."
            )
            wait_for_enter()
            continue

        contacts = action(contacts)
        wait_for_enter()


def main() -> int:
    """
    Runs the Contact Manager program.

    Loads contacts from the JSON file on startup and provides an interactive
    menu. Changes are saved after every operation, so pressing Ctrl+C at any
    prompt exits without losing data.

    Returns:
        The process exit code: 0 on success, 1 if contacts could not be loaded.
    """
    try:
        contacts, warning = load_contacts()
    except OSError as error:
        print_error(f"Could not load your contacts, so the app will close. {error}")
        return 1

    try:
        if warning:
            print_message(f"\nWarning: {warning}")
            wait_for_enter()
        run_menu_loop(contacts)
    except (KeyboardInterrupt, EOFError):
        print_message(f"\n{GOODBYE_MESSAGE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
