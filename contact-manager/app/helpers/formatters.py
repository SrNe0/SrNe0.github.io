"""
Formatting helpers.

This module provides functions to format contacts for display.
"""

from app.configs.settings import MENU_WIDTH
from app.models.contact import Contact


def format_contact(contact: Contact) -> str:
    """
    Formats a single contact for display.

    Args:
        contact: Contact information with keys: id, name, phone, email.

    Returns:
        Formatted string representation of the contact.
    """
    lines = [
        f"\nID: {contact['id']}",
        f"Name: {contact['name']}",
        f"Phone: {contact['phone']}",
        f"Email: {contact['email']}",
        "-" * MENU_WIDTH,
    ]
    return "\n".join(lines)


def format_contact_list(contacts: list[Contact]) -> str:
    """
    Formats a list of contacts for display.

    Args:
        contacts: List of contacts.

    Returns:
        Formatted string representation of all contacts.
    """
    lines = []
    for contact in contacts:
        lines.append(f"\n[{contact['id']}] {contact['name']}")
        lines.append(f"    Phone: {contact['phone']}")
        lines.append(f"    Email: {contact['email']}")
    return "\n".join(lines)
