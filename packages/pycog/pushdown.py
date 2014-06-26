"""Non-deterministic pushdown automata"""

from pycog.exceptions import StateStackEmpty
import pycog.statemachine as sm


class push_state(sm.state):
    """
    State decorator for states that push the state stack.
    """

    def __init__(self, name, resume, state_dict=None, **kw_args):
        if state_dict != None:
            assert type(state_dict) is dict
        else:
            state_dict = dict()

        state_dict['_push_state'] = True
        state_dict['_resume_state'] = resume
        super().__init__(name, state_dict, **kw_args)


class pop_state(sm.state):
    """
    State decorator for states that pop the state stack.
    """

    def __init__(self, name, state_dict=None, **kw_args):
        if state_dict != None:
            assert type(state_dict) is dict
        else:
            state_dict = dict()

        state_dict['_pop_state'] = True
        super().__init__(name, state_dict, **kw_args)


class Frame:
    """
    A stack frame.

    This is a name space that is scoped according to stack pushes and pops.
    The 'state' attribute is reserved for the PushDown class, other attributes
    may be added by applications.
    """
    pass


class PushDown(sm.StateMachine):
    """
    Non-deterministic pushdown automata
    """

    def __init__(self, **kw_args):
        super().__init__(**kw_args)

        self.stack = []
        self._frame = Frame()
        self.on_init_frame(self._frame)

    @property
    def top_frame(self):
        """
        Access the frame on the top of the stack.

        Raises:
            IndexError: The stack is empty.
        """
        if self.stack_empty: raise StateStackEmpty()
        return self.stack[-1]

    @property
    def active_frame(self):
        """
        Access the active frame.
        """
        return self._frame

    @property
    def stack_empty(self):
        """
        Return whether the stack is empty or not.
        """
        return len(self.stack) == 0

    def add_state(self, s_name, resume=None, pop=False, **kw_args):
        """
        Add a new state or replace an existing one.

        Args:
            s_name: Name of the state, must be hashable.
            resume: Specifies that this is a push state that should resume to
                the specified state.
            pop: Specifies that this is a pop state.
            state_data: Data associated with this state.
            activity: Callable to execute when in the state.  The call
                signature is activity(statemachine, current_state, state)
        """
        if resume:
            assert not pop, "A state may not be both a push_state and a "\
                    "pop_state."
        super().add_state(self, s_name, **kw_args)
        state_dict = self.state_dict(s_name)
        state_dict['_push_state'] = resume != None
        state_dict['_resume_state'] = resume
        state_dict['_pop_state'] = pop_state

    def _resume(self):
        """
        Resume a state suspended by a push.

        Calls the current state's on_resume handler, and then transitions to
        the resume state.
        """
        self.on_resume_state(self._current_state)

        record = self._state_records[self.current_state]
        next_state = record.state_dict['_resume_state']
        super()._do_transition(next_state)

    def on_resume_state(self, s_name):
        """
        Handle notification that a state has been resumed after being
            suspended.

        Args:
            s_name: Name of the state that has been resumed.

        Derived classes implementing this handler should call
        super().on_resume_state.
        """
        pass

    def _suspend(self):
        """Call the current state's on_suspend handler."""

        if hasattr(self, '_bt_suspend_state'):
            self._bt_suspend_state()
        self.on_suspend_state(self._current_state)

    def on_enter_state(self, s_name):
        """
        Notification that a state has been entered.

        Args:
            s_name: Name of the state that has been entered.

        This overload records the current state in the top stack frame.

        Derived classes implementing this handler should call
        super().on_enter_state().
        """
        self.active_frame.state = s_name
        super().on_enter_state(s_name)

    def on_suspend_state(self, s_name):
        """
        Notification that a state has been suspended.

        Args:
            s_name: is the name of the state being suspended.

        Derived classes implementing this handler should call
        super().on_suspend_state().
        """
        pass

    def on_init_frame(self, frame):
        """
        Handle a notification that a new stack is being initialized.

        Args:
            frame: The Frame instance being initialized.
        """
        pass

    def _push(self):
        """
        Push the current state onto the stack and enter a new state.

        Args:
            next_state: Initial state of the new stack frame.

        Raises:
            KeyError if next_state is not a known state name.

        """

        self._suspend()
        self.stack.append(self._frame)
        self._frame = Frame()
        self.on_init_frame(self._frame)
        self._frame.state = None

    def _pop(self):
        """
        Pop the last suspended state from the stack and resume it.
        """

        if self.stack_empty: raise StateStackEmpty()
        self._exit()
        self._frame = self.stack.pop()
        self._current_state = self._frame.state
        self._resume()

    def _transition(self):
        """
        Handle the details of transitioning.

        This overload checks for push and pop states before transitioning.
        """
        state_dict = super().state_dict(self.current_state)
        try:
            if state_dict['_push_state']:
                self._push()
        except KeyError:
            pass

        try:
            if state_dict['_pop_state']:
                self._pop()
                return
        except KeyError:
            pass

        super()._transition()

    def accept_test(self):
        if len(self.stack) > 0:
            return False
        return super().accept_test()

