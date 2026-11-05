"""
Contacts business logic service.

This module contains the CRUD operations and business rules for contacts. The
functions are pure: they do not read input, print output, or access files, and
they return new lists instead of changing the ones they receive.
"""

from typing import Optional

from app.configs.settings import NOT_PROVIDED
from app.models.contact import Contact, create_contact
from app.utils.validators import is_valid_email, is_valid_name, is_valid_phone

INVALID_NAME_MESSAGE = "Name cannot be empty."
INVALID_PHONE_MESSAGE = "Phone must contain digits only (0-9)."
INVALID_EMAIL_MESSAGE = "Email must have the form name@domain.com."

SEARCH_FIELDS = ("name", "phone", "email")


def _validate_fields(name: Optional[str], phone: str, email: str) -> None:
    """
    Validates the fields of a contact. Empty optional fields are allowed.

    Args:
        name: Contact name, or None if it is not being changed.
        phone: Phone number, or an empty string.
        email: Email address, or an empty string.

    Raises:
        ValueError: If a field is invalid.
    """
    if name is not None and not is_valid_name(name):
        raise ValueError(INVALID_NAME_MESSAGE)
    if phone and not is_valid_phone(phone):
        raise ValueError(INVALID_PHONE_MESSAGE)
    if email and not is_valid_email(email):
        raise ValueError(INVALID_EMAIL_MESSAGE)


def generate_id(contacts: list[Contact]) -> int:
    """
    Generates a new ID that no current contact is using.

    Uses max(existing_ids) + 1, so an ID can be assigned again only if the
    contact with the highest ID was deleted.

    Args:
        contacts: Current list of contacts.

    Returns:
        A new unique contact ID.
    """
    return max((contact["id"] for contact in contacts), default=0) + 1


def find_contact_by_id(
    contacts: list[Contact], contact_id: int
) -> Optional[Contact]:
    """
    Finds a contact by its ID.

    Args:
        contacts: List of contacts.
        contact_id: Contact ID to search for.

    Returns:
        The contact if found, otherwise None.
    """
    for contact in contacts:
        if contact["id"] == contact_id:
            return contact
    return None


def search_contacts(contacts: list[Contact], query: str) -> list[Contact]:
    """
    Finds contacts by exact ID or partial match on name, phone, or email.

    Matching ignores case, and the NOT_PROVIDED placeholder never matches.

    Args:
        contacts: List of contacts.
        query: Text to search for.

    Returns:
        The matching contacts.
    """
    term = query.strip().casefold()
    if not term:
        return []

    matches = []
    for contact in contacts:
        values = [
            contact[field]
            for field in SEARCH_FIELDS
            if contact[field] != NOT_PROVIDED
        ]
        if term == str(contact["id"]) or any(
            term in value.casefold() for value in values
        ):
            matches.append(contact)
    return matches


def find_duplicates(
    contacts: list[Contact],
    phone: str = "",
    email: str = "",
    exclude_id: Optional[int] = None,
) -> list[Contact]:
    """
    Finds contacts that already use a phone number or email address.

    Args:
        contacts: List of contacts.
        phone: Phone number to check. Empty values are ignored.
        email: Email address to check, ignoring case. Empty values are ignored.
        exclude_id: ID of a contact to skip, such as the one being updated.

    Returns:
        The contacts that share the phone number or email address.
    """
    return [
        contact
        for contact in contacts
        if contact["id"] != exclude_id
        and (
            (phone and contact["phone"] == phone)
            or (email and contact["email"].casefold() == email.casefold())
        )
    ]


def add_contact(
    contacts: list[Contact], name: str, phone: str = "", email: str = ""
) -> tuple[list[Contact], Contact]:
    """
    Adds a new contact.

    Args:
        contacts: Current contact list.
        name: Contact name.
        phone: Phone number, or an empty string if not provided.
        email: Email address, or an empty string if not provided.

    Returns:
        A tuple with the new contact list and the created contact.

    Raises:
        ValueError: If a field is invalid.
    """
    _validate_fields(name, phone, email)
    new_contact = create_contact(generate_id(contacts), name, phone, email)
    return [*contacts, new_contact], new_contact


def update_contact(
    contacts: list[Contact],
    contact_id: int,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> tuple[list[Contact], Contact]:
    """
    Updates an existing contact.

    A field set to None keeps its current value. An empty phone or email clears
    the field.

    Args:
        contacts: Current contact list.
        contact_id: ID of the contact to update.
        name: New name, or None to keep the current one.
        phone: New phone number, or None to keep the current one.
        email: New email address, or None to keep the current one.

    Returns:
        A tuple with the new contact list and the updated contact.

    Raises:
        LookupError: If no contact has the given ID.
        ValueError: If a field is invalid.
    """
    current = find_contact_by_id(contacts, contact_id)
    if current is None:
        raise LookupError(f"Contact with ID {contact_id} not found.")

    _validate_fields(name, phone or "", email or "")

    updated = dict(current)
    if name is not None:
        updated["name"] = name
    if phone is not None:
        updated["phone"] = phone or NOT_PROVIDED
    if email is not None:
        updated["email"] = email or NOT_PROVIDED

    new_contacts = [
        updated if contact["id"] == contact_id else contact for contact in contacts
    ]
    return new_contacts, updated


def delete_contact(
    contacts: list[Contact], contact_id: int
) -> tuple[list[Contact], Contact]:
    """
    Deletes a contact.

    Args:
        contacts: Current contact list.
        contact_id: ID of the contact to delete.

    Returns:
        A tuple with the new contact list and the deleted contact.

    Raises:
        LookupError: If no contact has the given ID.
    """
    deleted = find_contact_by_id(contacts, contact_id)
    if deleted is None:
        raise LookupError(f"Contact with ID {contact_id} not found.")

    return [contact for contact in contacts if contact["id"] != contact_id], deleted
