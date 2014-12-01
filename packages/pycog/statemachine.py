"""State machine"""

import inspect

from pycog.exceptions import Accept, Reject, Backtrack

class _StateRecord:
    """Information about a state."""

    def __init__(self, name, state_dict, activity=None, accepting=False,
                 guard=lambda fsm:True):
        self.name = name
        if state_dict == None:
            self.state_dict = dict()
        else:
            self.state_dict = state_dict
        self.activity = activity
        self.state_dict['_accepting'] = accepting

        # Names of available transitions.  Order is important for stability.
        self.transitions = []

        # current_state -> test(sm, exiting, entering)
        self.transition_info = dict()

        # guard function.  Determines if the state can be entered.
        self.guard = guard;

class _TransitionRecord:
    """Information about a transition"""

    def __init__(self, test, label=None):
        self.test = test
        self.label = label

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
            return True

        # Another way to specify transitions.  The lambda function takes
        # a StateMachine instance as it's `sm` argument.
        @state('q', transitions=[
            ('r', lambda sm, cur_state, trans_state: ...),
            ('s', lambda sm, cur_state, trans_state: ...)])
    """

    def __init__(self, name, state_dict=None, transitions=None,
                 accepting=False, label=None,  **kw_args):
        if __debug__:
            if state_dict != None:
                assert type(state_dict) is dict

        super().__init__(**kw_args)
        self.record = _StateRecord(name, state_dict, accepting=accepting)
        if transitions != None:
            for transition in transitions:
                if type(transition) is tuple:
                    if len(transition) == 2:
                        target_s_name, test = transition
                    elif len(transition) == 1:
                        # This allows a way of specifying transition keys that
                        # are tuples without a test, "(x,y),".  This way (x,y)
                        # is considered the transition, and the test is
                        # unspecified.  "(x, y)" would take x as the transition
                        # and y as the transition test.
                        target_s_name, = transition
                        test = transition_always
                    else:
                        raise ValueError("Invalid transition specification.")
                else:
                    target_s_name = transition
                    test = transition_always

                self.record.transitions.append(target_s_name)
                self.record.transition_info[target_s_name] = \
                        _TransitionRecord(test, label)

    def __call__(self, activity):
        self.record.activity = activity
        return self

    def transition(self, target_s_name, label=None):
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
            """
            Decorator helper for transitions.
            """
            nonlocal self, target_s_name

            def _trans_test(fsm, cur_state, next_state):
                """
                Adapter for one-parameter transition tests.
                """
                return method(fsm)

            self.record.transitions.append(target_s_name)
            self.record.transition_info[target_s_name] =\
                    _TransitionRecord(_trans_test, label)

            return self

        return _transition_setter

    def guard(self, method):
        """
        Decorator for state guards.

        A state guard should return True if the state may be entered, false
        otherwise.
        """
        self.record.guard = method
        return self

def transition_always(fsm, cur_state, next_state):
    """
    Convenience transition test -- always transition.
    """
    return True


class StateMachine:
    """State machine framework"""

    def __init__(self, initial=None, **kw_args):

        super().__init__(**kw_args)


        # These help get from the name to the state and vice-versa.
        self._state_records = dict()

        # Create states for items created with the 'state' decorator
        for attr_name in dir(self):
            attr = inspect.getattr_static(self, attr_name)
            if isinstance(attr, state):
                self._state_records[attr.record.name] = attr.record

        if initial:
            self.set_initial_state(initial)
        else:
            self._current_state = None

    def set_initial_state(self, s_name):
        """
        Set the initial state, if not done in the initializer.

        One way or another, the initial state must be done before running the
        state machine.
        """
        self._current_state = s_name
        self._initial = s_name
        self.state_dict(s_name)['_initial'] = True

    @property
    def current_state(self):
        """Return the current state of the FSM."""
        return self._current_state
    @current_state.setter
    def current_state(self, value):
        self._current_state = value

    def state_dict(self, s_name):
        """
        Access the dictionary associated with the state.

        Args:
            s_name: Name of the state.

        Returns:
            The dictionary associated with s_name.

        Raises:
            KeyError: s_name is not a registered state.
        """
        return self._state_records[s_name].state_dict

    # State forwards
    def _enter(self):
        """Call the current state's on_enter handler."""

        self.on_enter_state(self._current_state)

    def on_enter_state(self, s_name):
        """
        Notification that a state has been entered.

        Args:
            s_name: Name of the state that has been entered.

        Derived classes implementing this handler should call
        super().on_enter_state().
        """
        pass

    def _exit(self):
        """Call the current state's on_exit handler."""

        self.on_exit_state(self._current_state)

    def on_exit_state(self, s_name):
        """
        Notification that a state has been exited.

        Args:
            s_name: is the name of the state being exited.

        Derived classes implementing this handler should call
        super().on_exit_state().
        """
        pass

    def on_no_transition(self, s_name):
        """
        Handle the no_transition notification.

        The on_no_transition handler is called when a state has no acceptable
        transitions available.

        Args:
            s_name: is the name of the state being exited.

        Derived classes implementing this handler should call
        super().on_no_transition().
        """
        msg = "Cannot transition from state {st}"
        raise Reject(msg.format(st=self.current_state))

    def add_state(self, s_name, state_data=None, activity=None,
                  guard=lambda fsm:True, accepting=False):
        """
        Add a new state or replace an existing one.

        Args:
            s_name: Name of the state, must be hashable.
            state_data: Data associated with this state.
            activity: Callable to execute when in the state.  The call
                signature is activity(statemachine, current_state, state)
        """
        record = _StateRecord(s_name, state_data, activity, guard=guard,
                              accepting=accepting)
        self._state_records[s_name] = record

    def remove_state(self, s_name):
        """
        Remove a state.

        Args:
            s_name: Name of the state to remove.
        """
        del self._state_records[s_name]

    def add_transition(self, exiting, entering,
                       test=transition_always, label=None):
        """
        Add a transition from one state to another.

        Args:
            exiting: Name of the state for which transition is exiting.
            entering: Name of the state for which transition is entering.
            test: Function to test if the transition is allowed to be made.
            label: Label for this transtion in diagrams.

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
        if entering not in record.transition_info:
            record.transitions.append(entering)

        record.transition_info[entering] = _TransitionRecord(test, label)

    def remove_transition(self, exiting, entering):
        """
        Remove a transition.

        Args:
            exiting: Name of the state for which transition is exiting.
            entering: Name of the state for which transition is entering.

        Raises:
            KeyError

        TODO: Needs test.
        """
        record = self._state_records[exiting]
        record.transition.remove(entering)
        del record.transition_info[entering]

    def on_pre_select_transition(self, s_name, candidate_s_names):
        """
        Handle a notification that a transition is about to be selected.

        This handler may be useful to record the list of transitions.

        Args:
            s_name: The name of the current state.
            candidate_s_names: List of transition candidates which have passed
                any applicable transition tests.

        Derived classes implementing this handler should call
        super().on_pre_select_transition().
        """
        pass

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

        Derived classes implementing this handler should call
        super().on_transition().
        """
        pass

    def _do_transition(self, next_state):
        """Final execution of a transition."""
        self._current_state = next_state
        self._enter()
        
    def _transition_multiple(self, allowed_transitions):
        """
        """
        self.on_pre_select_transition(self.current_state, allowed_transitions)
        next_state = self.select_transition(self.current_state,
                                            allowed_transitions)
        self.on_transition(self.current_state, next_state)

        self._do_transition(next_state)

    def _transition(self):
        """
        Handle the details of transitioning.

        For internal use.
        """
        record = self._state_records[self.current_state]

        # Transitioning
        allowed_transitions = []
        for next_trans in record.transitions:
            if record.transition_info[next_trans].test(self,
                                                       self.current_state,
                                                       next_trans):
                next_record = self._state_records[next_trans]
                if next_record.guard(self):
                    allowed_transitions.append(next_trans)

        if not allowed_transitions:
            self.on_no_transition(self.current_state)
            return

        self._exit()

        self._transition_multiple(allowed_transitions)

    def _do_activity(self):
        """
        Run the activity associated with the state.

        For internal use.
        """
        if self.current_state in self._state_records:
            activity = self._state_records[self.current_state].activity
            if activity == None:
                return

            activity(self)

    def _run(self):
        """
        Helper function for run.

        This is the heart of run(), but without the exception handling.  _run
        can be called recursively, e.g. in pushdown automata.
        """
        assert self._current_state, "Initial state not set."
        self._enter()
        while True:
            try:
                self._do_activity()
                self._transition()

            except Backtrack:
                # TODO: Handle this without referencing backtracking.
                if not self._backtrack():
                    self.on_exhausted()

                    raise Reject("Backtracking exhausted.")

    def run(self):
        """Run the state machine"""

        try:
            self._run()

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

        Derived classes implementing this handler should call
        super().on_accept().
        """
        pass

    def on_reject(self, exc):
        """
        Called when the input has been rejected.

        Args:
            exc: Exception triggering this event.

        Derived classes implementing this handler should call
        super().on_reject().
        """
        pass

    def accept_test(self):
        return True

    # Container protocol special methods

    def __len__(self):
        """Return the number of known states."""
        return len(self._state_records)

    def __contains__(self, s_name):
        """Test if a state is in the state machine."""

        return s_name in self._state_records


if __name__ == '__main__':
    import sys
    sys.stderr.write("Pycog statemachine.py module is not intended to run "
                     "standalone.")

