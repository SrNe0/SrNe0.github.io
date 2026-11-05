"""
Console utilities.

This module provides utility functions for console operations.
"""


def clear_screen() -> None:
    """
    Clears the console screen using ANSI escape codes.

    Note:
        Works in most terminals that support ANSI escape sequences.
    """
    print("\033[2J\033[H", end="")
