"""
Interactive contact flows.

This module connects the console with the business logic. Each flow prompts the
user, calls the services, saves the result, and reports what happened. Every
flow receives the current contact list and returns the list to keep using, which
stays unchanged if a save fails.
"""

from app.configs.settings import CLEAR_FIELD_VALUE
from app.db.csv_export import export_contacts_csv
from app.db.json_store import save_contacts
from app.helpers.formatters import format_contact, format_contact_list
from app.interface.menu import (
    print_error,
    print_message,
    prompt_confirmation,
    prompt_contact_id,
    prompt_optional_field,
    prompt_string,
)
from app.models.contact import Contact
from app.services import contacts_service as service
from app.utils.validators import is_valid_email, is_valid_phone


def _persist(contacts: list[Contact]) -> bool:
    """
    Saves contacts and reports any failure to the user.

    Args:
        contacts: Contacts to save.

    Returns:
        True if the contacts were saved.
    """
    try:
        save_contacts(contacts)
    except OSError as error:
        print_error(f"Could not save your changes, so they were undone. {error}")
        return False
    return True


def _confirm_if_duplicate(duplicates: list[Contact]) -> bool:
    """
    Asks whether to continue when a phone number or email is already in use.

    Args:
        duplicates: Contacts that share the phone number or email.

    Returns:
        True if there are no duplicates or the user chose to continue.
    """
    if not duplicates:
        return True

    print_message("\nWarning: This phone or email is already used by:")
    print_message(format_contact_list(duplicates))
    return prompt_confirmation("\nSave anyway? (yes/no): ")


def add_contact_flow(contacts: list[Contact]) -> list[Contact]:
    """
    Adds a new contact.

    Args:
        contacts: Current contact list.

    Returns:
        The contact list to keep using.
    """
    print_message("\n--- ADD NEW CONTACT ---")

    name = prompt_string("Name: ")
    if not name:
        print_error(service.INVALID_NAME_MESSAGE)
        return contacts

    phone = prompt_optional_field(
        "Phone (digits only, optional): ",
        is_valid_phone,
        service.INVALID_PHONE_MESSAGE,
    )
    email = prompt_optional_field(
        "Email (optional): ", is_valid_email, service.INVALID_EMAIL_MESSAGE
    )

    if not _confirm_if_duplicate(service.find_duplicates(contacts, phone, email)):
        print_message("\nContact not added.")
        return contacts

    new_contacts, contact = service.add_contact(contacts, name, phone, email)
    if not _persist(new_contacts):
        return contacts

    print_message(f"\nContact '{contact['name']}' added successfully!")
    return new_contacts


def view_all_contacts_flow(contacts: list[Contact]) -> list[Contact]:
    """
    Displays all contacts.

    Args:
        contacts: List of contacts.

    Returns:
        The contact list, unchanged.
    """
    print_message("\n--- ALL CONTACTS ---")

    if not contacts:
        print_message("No contacts found.")
        return contacts

    print_message(format_contact_list(contacts))
    return contacts


def search_contacts_flow(contacts: list[Contact]) -> list[Contact]:
    """
    Searches contacts by ID, name, phone, or email and displays the matches.

    Args:
        contacts: List of contacts.

    Returns:
        The contact list, unchanged.
    """
    print_message("\n--- SEARCH CONTACTS ---")

    if not contacts:
        print_message("No contacts available.")
        return contacts

    query = prompt_string("Search by ID, name, phone or email: ")
    if not query:
        print_error("Search text cannot be empty.")
        return contacts

    matches = service.search_contacts(contacts, query)
    if not matches:
        print_message(f"No contacts match '{query}'.")
        return contacts

    print_message(format_contact_list(matches))
    return contacts


def update_contact_flow(contacts: list[Contact]) -> list[Contact]:
    """
    Updates an existing contact by ID.

    The user may press Enter to keep the current value of each field, or enter
    CLEAR_FIELD_VALUE to clear the phone or email.

    Args:
        contacts: Current contact list.

    Returns:
        The contact list to keep using.
    """
    print_message("\n--- UPDATE CONTACT ---")

    if not contacts:
        print_message("No contacts available.")
        return contacts

    contact_id = prompt_contact_id("Enter contact ID: ")
    contact = service.find_contact_by_id(contacts, contact_id)
    if contact is None:
        print_message(f"Contact with ID {contact_id} not found.")
        return contacts

    print_message("\nCurrent information:")
    print_message(format_contact(contact))

    print_message(
        "\nEnter new values (press Enter to keep current, "
        f"'{CLEAR_FIELD_VALUE}' to clear phone or email):"
    )
    name = prompt_string("Name: ")
    phone = prompt_optional_field(
        "Phone (digits only): ",
        is_valid_phone,
        service.INVALID_PHONE_MESSAGE,
        allow_clear=True,
    )
    email = prompt_optional_field(
        "Email: ", is_valid_email, service.INVALID_EMAIL_MESSAGE, allow_clear=True
    )

    if not (name or phone or email):
        print_message("\nNo changes made.")
        return contacts

    new_phone = "" if phone == CLEAR_FIELD_VALUE else phone
    new_email = "" if email == CLEAR_FIELD_VALUE else email
    duplicates = service.find_duplicates(
        contacts, new_phone, new_email, exclude_id=contact_id
    )
    if not _confirm_if_duplicate(duplicates):
        print_message("\nContact not updated.")
        return contacts

    new_contacts, _ = service.update_contact(
        contacts,
        contact_id,
        name=name or None,
        phone=new_phone if phone else None,
        email=new_email if email else None,
    )
    if not _persist(new_contacts):
        return contacts

    print_message("\nContact updated successfully!")
    return new_contacts


def delete_contact_flow(contacts: list[Contact]) -> list[Contact]:
    """
    Deletes a contact by ID after user confirmation.

    Args:
        contacts: Current contact list.

    Returns:
        The contact list to keep using.
    """
    print_message("\n--- DELETE CONTACT ---")

    if not contacts:
        print_message("No contacts available.")
        return contacts

    contact_id = prompt_contact_id("Enter contact ID: ")
    contact = service.find_contact_by_id(contacts, contact_id)
    if contact is None:
        print_message(f"Contact with ID {contact_id} not found.")
        return contacts

    print_message("\nContact to delete:")
    print_message(format_contact(contact))

    if not prompt_confirmation("Are you sure? (yes/no): "):
        print_message("\nDeletion cancelled.")
        return contacts

    new_contacts, deleted = service.delete_contact(contacts, contact_id)
    if not _persist(new_contacts):
        return contacts

    print_message(f"\nContact '{deleted['name']}' deleted.")
    return new_contacts


def export_contacts_flow(contacts: list[Contact]) -> list[Contact]:
    """
    Exports all contacts to a CSV file.

    Args:
        contacts: List of contacts.

    Returns:
        The contact list, unchanged.
    """
    print_message("\n--- EXPORT TO CSV ---")

    if not contacts:
        print_message("No contacts available.")
        return contacts

    try:
        path = export_contacts_csv(contacts)
    except OSError as error:
        print_error(f"Could not export contacts. {error}")
        return contacts

    print_message(f"\n{len(contacts)} contact(s) exported to {path}")
    return contacts
