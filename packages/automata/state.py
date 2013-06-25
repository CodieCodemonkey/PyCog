"""State class"""

def _null_handler(machine):
    pass

class State:
    """Represents a state in a state machine."""

    def __init__(self, name, method):
        self.name = name
        self.while_active = method
        self._transitions = []

        self.on_enter = _null_handler
        self.on_exit = _null_handler

    def transition(self, target_state):
        """
        Transition test decorator

        target_state -- Name of the target state
        """

        def _transition_setter(method):
            nonlocal self, target_state

            self._transitions.append((method, target_state))
            return self

        return _transition_setter

    def copy_transitions(self, state):
        have = set([s for (_, s) in self._transitions])
        for (m, s) in state._transitions:
            if s not in have:
                self._transitions.append((m, s))

    def add_transition(self, state_name, predicate):
        self._transitions.append((predicate, state_name))

    def no_transition(self, method):
        """"No transition" event handler decorator"""
        self.no_transition = method
        return self

    def enter(self, method):
        """Enter handler decorator"""
        self.on_enter = method
        return self

    def exit(self, method):
        """Exit handler decorator"""
        self.on_exit = method
        return self

class state:
    """
    State method decorator.

    Creates a state from a method.

    name -- Name of the state (a string).
    cls -- Optional State-derived class to instatiate.  Must have the same
        constructor signature as State.
    """

    def __init__(self, name, cls = State):
        self._name = name
        self._cls = cls

    def __call__(self, method):
        st = self._cls(self._name, method)
        return st
