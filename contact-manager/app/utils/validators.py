"""
Input validation utilities.

This module provides pure validation functions. They do not read input or print
output, so any interface can reuse them.
"""

import re
from typing import Optional

EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s.]+")


def is_valid_name(name: str) -> bool:
    """
    Checks that a contact name is not empty.

    Args:
        name: Name to validate.

    Returns:
        True if the name contains visible characters.
    """
    return bool(name.strip())


def is_valid_phone(phone: str) -> bool:
    """
    Checks that a phone number contains only the digits 0-9.

    Args:
        phone: Phone number to validate.

    Returns:
        True if the phone number is valid.
    """
    return phone.isascii() and phone.isdigit()


def is_valid_email(email: str) -> bool:
    """
    Checks that an email address has the form name@domain.tld.

    Args:
        email: Email address to validate.

    Returns:
        True if the email address is valid.
    """
    return EMAIL_PATTERN.fullmatch(email) is not None


def parse_contact_id(raw_id: str) -> Optional[int]:
    """
    Converts user input to a contact ID.

    Args:
        raw_id: Text entered by the user.

    Returns:
        The positive integer ID, or None if the text is not a valid ID.
    """
    if not (raw_id.isascii() and raw_id.isdigit()):
        return None
    contact_id = int(raw_id)
    return contact_id if contact_id > 0 else None
