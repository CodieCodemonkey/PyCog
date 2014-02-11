"""State machine"""

import inspect

from pycog.exceptions import *

class _StateRecord:
    """Information about a state."""

    def __init__(self, name, data, activity=None):
        self.name = name
        self.data = data
        self.activity = activity

        # Names of available transitions.  Order is important for stability.
        self.transitions = []

        # current_state -> test(sm, exiting, entering)
        self.transition_tests = dict()

class state:
    """State decorator

    Example:
        @state('p')
        def p(self):
            '''In state p'''
            pass
        @transition('q')
        def p(self):
            '''Test for transition to q.'''
            ...
    """

    def __init__(self, name, data=None, **kw_args):
        super().__init__(**kw_args)
        self.record = _StateRecord(name, data)

    def __call__(self, activity):
        self.record.activity = activity
        return self

    def transition(self, target_s_name):
        """
        Transition test decorator

        Args:
            target_s_name: Name of the target state

        Example:
            @state('p')
            def p(self):
                '''In state p'''
                pass
            @transition('q')
            def p(self):
                '''Test for transition to q.'''
                ...
        """

        def _transition_setter(method):
            nonlocal self, target_s_name

            def _trans_test(fsm, cur_state, next_state):
                return method(fsm)

            self.record.transitions.append(target_s_name)
            self.record.transition_tests[target_s_name] = _trans_test

            return self

        return _transition_setter

class StateMachine:
    """State machine framework"""

    def __init__(self, initial, **kw_args):

        super().__init__(**kw_args)

        # Name of the current state, not the state itself.
        self._current_state = initial
        self._initial = initial

        # These help get from the name to the state and vice-versa.
        self._state_records = dict()

        # Create states for items created with the 'state' decorator
        for attr_name in dir(self):
            attr = inspect.getattr_static(self, attr_name)
            if type(attr) == state:
                self._state_records[attr.record.name] = attr.record

    @property
    def current_state(self):
        """Return the current state of the FSM."""
        return self._current_state
    @current_state.setter
    def current_state(self, value):
        self._current_state = value

    def get_state_data(self, s_name):
        """
        Get user-defined data associated with a state.

        Args:
            s_name: Name of the state.

        Returns:
            User defined data associated with this state, or None.

        Raises:
            KeyError if s_name is not a known state name.
        """
        return self._state_records[s_name].data

    # State forwards
    def _enter(self):
        """Call the current state's on_enter handler."""

        if hasattr(self, '_bt_on_enter_state'): self._bt_on_enter_state()
        self.on_enter_state(self._current_state)

    def on_enter_state(self, s_name):
        """
        Notification that a state has been entered.

        Args:
            s_name: Name of the state that has been entered.
        """
        pass

    def _exit(self):
        """Call the current state's on_exit handler."""

        if hasattr(self, '_bt_exit_state'): self._bt_exit_state()
        self.on_exit_state(self._current_state)

    def on_exit_state(self, s_name):
        """
        Notification that a state has been exited.

        Args:
            s_name: is the name of the state being exited.
        """
        pass

    def no_transition(self, s_name):
        """
        Call the no_transition handler.

        The no_transition handler can be used to raise a custom exception,
        including Accept or Reject.  If no exception is raise, Reject will be
        automatically raised following the call.

        Args:
            s_name: is the name of the state being exited.
        """
        pass

    def add_state(self, s_name, state_data=None, activity=None):
        """
        Add a new state or replace an existing one.

        Args:
            s_name: Name of the state, must be hashable.
            state_data: Data associated with this state.
            activity: Callable to execute when in the state.  The call
                signature is activity(statemachine, current_state, state)
        """
        record = _StateRecord(s_name, state_data, activity)
        self._state_records[s_name] = record

    def remove_state(self, s_name):
        """
        Remove a state.

        Args:
            s_name: Name of the state to remove.
        """
        del self._state_records[s_name]

    def add_transition(self, exiting, entering,
                       test=lambda fsm, exiting, entering: True):
        """
        Add a transition from one state to another.

        Args:
            exiting: Name of the state for which transition is exiting.
            entering: Name of the state for which transition is entering.
            test: Function to test if the transition is allowed to be made.

        test() should return True if the transition should be allowed, or False
        otherwise.

        Note:
            If the transition already exists it will be replaced.

        Raises:
            KeyError

        The test function will be called with three positional arguments:
            fsm: StateMachine instance that owns the vertices.
            exiting: The state being left.
            entering: The state being entered.
        """
        record = self._state_records[exiting]
        if entering not in record.transition_tests:
            record.transitions.append(entering)

        record.transition_tests[entering] = test

    def remove_transition(self, exiting, entering):
        """
        Remove a transition.

        Args:
            exiting: Name of the state for which transition is exiting.
            entering: Name of the state for which transition is entering.

        Raises:
            KeyError
        """
        record = self._state_records[self.exiting]
        record.transition.remove(entering)
        del record.transition_tests[entering]

    def select_transition(self, s_name, candidate_s_names):
        """
        Select a transition state from the list of qualifying states.

        Args:
            s_name: The name of the current state.
            candidate_s_names: List of transition candidates which have passed
                any applicable transition tests.

        Returns:
            The choice of state to receive the transition.
        """
        return candidate_s_names[0]

    def on_transition(self, exiting, entering):
        """
        Notification that a transition is in effect.

        This is called after on_exit for the exiting state, and before on_enter
        for the entering state.

        Args:
            exiting: State name of the previously active state.
            entering: State name of the next active state.
        """
        pass

    def _transition(self):
        """
        Handle the details of transitioning.

        For internal use.
        """
        record = self._state_records[self.current_state]

        # Transitioning
        allowed_transitions = []
        for next in record.transitions:
            if record.transition_tests[next](self, self.current_state, next):
                allowed_transitions.append(next)

        if len(allowed_transitions) == 0:
            if hasattr(self, "_backtrack"):
                if self._backtrack():
                    return
                else:
                    self.on_exhausted()

                    raise Reject("Backtracking exhausted.")
            else:
                self.no_transition(self.current_state)
                msg = "Cannot transition from state {st}"
                raise Reject(msg.format(st = self.current_state))

        self._exit()
        if hasattr(self, '_bt_select_transition'):
            next_state = self._bt_select_transition(allowed_transitions)
        else:
            next_state = self.select_transition(self.current_state,
                                                allowed_transitions)

        self.on_transition(self.current_state, next_state)

        self._current_state = next_state
        self._enter()

    def _do_activity(self):
        """
        Run the activity associated with the state.

        For internal use.
        """
        if self.current_state in self._state_records:
            activity = self._state_records[self.current_state].activity
            if activity == None: return

            activity(self)

    def run(self):
        """Run the state machine"""

        try:
            self._enter()
            while True:
                try:
                    self._do_activity()
                    self._transition()

                except Backtrack as exc:
                    if not self._backtrack():
                        self.on_exhausted()

                        raise Reject("Backtracking exhausted.")

        except Accept as exc:
            self._exit()
            self.on_accept(exc)
            return True
        except Reject as exc:
            self._exit()
            self.on_reject(exc)
            return False

    def on_accept(self, exc):
        """
        Called when the input has been accepted.

        Args:
            exc: Exception triggering this event.
        """
        pass

    def on_reject(self, exc):
        """
        Called when the input has been rejected.

        Args:
            exc: Exception triggering this event.
        """
        pass

if __name__ == '__main__':
    import sys
    sys.stderr.write("Pycog statemachine.py module is not intended to run "
                     "standalone.")

