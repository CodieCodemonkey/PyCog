"""
pycog exceptions.
"""

class NotImplemented(Exception):
    """
    Missing expected interface method.

    Raised when interface methods have not been implemented in concrete
    classes.
    """
    pass

class Accept(Exception):
    """
    Accept the input stream.
    """
    pass

class Reject(Exception):
    """
    Reject the input stream.
    """
    pass

class Backtrack(Exception):
    """
    Request backtracking
    """
    pass

class StateStackEmpty(Exception):
    """
    State stack is empty.
    """
    def __init__(self, msg = None):
        if msg == None:
            super().__init__("State stack is empty.")
        else:
            super().__init__(msg)

class PopState(Exception):
    """
    Request popping the state stack (in a PushDown)
    """
    pass

