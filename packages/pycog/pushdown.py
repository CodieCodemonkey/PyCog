"""Non-deterministic pushdown automata"""

from pycog.exceptions import PopState, StateStackEmpty
import pycog.statemachine as sm

class PushDown(sm.StateMachine):
    """
    Non-deterministic pushdown automata
    """

    def __init__(self, **kw_args):
        super().__init__(**kw_args)

        self.stack = []

    def _resume(self):
        """Call the current state's on_resume handler."""

        if hasattr(self, '_bt_on_resume_state'):
            self._bt_on_resume_state()
        self.on_resume_state(self._current_state)

    def on_resume_state(self, s_name):
        """
        Notification that a state has been resumed after being suspended.

        Args:
            s_name: Name of the state that has been resumed.
        """
        pass

    def _suspend(self):
        """Call the current state's on_suspend handler."""

        if hasattr(self, '_bt_suspend_state'):
            self._bt_suspend_state()
        self.on_suspend_state(self._current_state)

    def on_suspend_state(self, s_name):
        """
        Notification that a state has been suspended.

        Args:
            s_name: is the name of the state being suspended.
        """
        pass

    def push(self, new_state):
        """
        Push the current state onto the stack and enter a new state.

        Args:
            new_state: Initial state of the new stack frame.

        Raises:
            KeyError if new_state is not a known state name.

        """
        self._suspend()
        self.stack.append(self.current_state)

        self._current_state = new_state
        self._enter()
        self._run()

    def pop(self):
        """
        Pop the last suspended state from the stack and resume it.
        """
        raise PopState()

    def _do_activity(self):
        """
        Run the activity associated with the state.

        This overload captures and processes PopState exceptions.
        """
        try:
            super()._do_activity()
        except PopState:
            if len(self.stack) == 0: raise StateStackEmpty()
            self._exit()
            self._current_state = self.stack.pop()
            self._resume()

