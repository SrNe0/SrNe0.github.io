"""
Contact model functions.

This module provides functions to create and normalize contact dictionaries.
No classes are used; contacts are represented as dictionaries.
"""

from typing import Any, Optional

from app.configs.settings import NOT_PROVIDED

Contact = dict[str, Any]


def create_contact(contact_id: int, name: str, phone: str, email: str) -> Contact:
    """
    Creates a new contact dictionary.

    Args:
        contact_id: Unique identifier for the contact.
        name: Contact name.
        phone: Contact phone number. Empty values become NOT_PROVIDED.
        email: Contact email address. Empty values become NOT_PROVIDED.

    Returns:
        A dictionary representing a contact with keys: id, name, phone, email.
    """
    return {
        "id": contact_id,
        "name": name,
        "phone": phone if phone else NOT_PROVIDED,
        "email": email if email else NOT_PROVIDED,
    }


def _coerce_id(raw_id: Any) -> int:
    """
    Converts a stored ID to a positive integer.

    Args:
        raw_id: ID value read from storage.

    Returns:
        The positive integer ID, or 0 if the value cannot be used as an ID.
    """
    if isinstance(raw_id, int) and not isinstance(raw_id, bool) and raw_id > 0:
        return raw_id
    if isinstance(raw_id, str) and raw_id.isascii() and raw_id.isdigit():
        return int(raw_id) if int(raw_id) > 0 else 0
    return 0


def _coerce_optional_field(value: Any) -> str:
    """
    Converts a stored optional field to its text representation.

    Args:
        value: Phone or email value read from storage.

    Returns:
        The value as stripped text, or NOT_PROVIDED if it is empty or missing.
    """
    if value is None:
        return NOT_PROVIDED
    return str(value).strip() or NOT_PROVIDED


def normalize_contact(raw_contact: Any) -> Optional[Contact]:
    """
    Ensures a stored contact has every required field.

    An unusable ID is returned as 0 so the caller can assign a new one.

    Args:
        raw_contact: Value read from storage.

    Returns:
        The normalized contact, or None if the value is not a dictionary or
        has no usable name.
    """
    if not isinstance(raw_contact, dict):
        return None

    name = raw_contact.get("name")
    if not isinstance(name, str) or not name.strip():
        return None

    return create_contact(
        _coerce_id(raw_contact.get("id")),
        name.strip(),
        _coerce_optional_field(raw_contact.get("phone")),
        _coerce_optional_field(raw_contact.get("email")),
    )


def normalize_contacts(raw_contacts: list[Any]) -> tuple[list[Contact], int]:
    """
    Normalizes stored contacts and repairs missing or duplicated IDs.

    Args:
        raw_contacts: Values read from storage.

    Returns:
        A tuple with the normalized contacts and the number of records that
        could not be recovered.
    """
    normalized = [normalize_contact(raw_contact) for raw_contact in raw_contacts]
    contacts = [contact for contact in normalized if contact is not None]

    next_id = max((contact["id"] for contact in contacts), default=0) + 1
    seen_ids = set()
    for contact in contacts:
        if contact["id"] == 0 or contact["id"] in seen_ids:
            contact["id"] = next_id
            next_id += 1
        seen_ids.add(contact["id"])

    return contacts, len(raw_contacts) - len(contacts)
