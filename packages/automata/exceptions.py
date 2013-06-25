"""Exceptions for module automata"""

class NotImplemented(Exception):
    """
    Raised when interface methods have not been implemented in concrete
    classes.
    """
    pass

class Accept(Exception):
    """Accept the input stream."""
    pass

class Reject(Exception):
    """Reject the input stream."""
    pass

class Backtrack(Exception):
    """Request backtracking"""
    pass

