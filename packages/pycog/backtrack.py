"""Support for back-tracking in state machines"""

from pycog.statemachine import StateMachine
import itertools

def _track_format(occ):
    """
    Format one StateOccurrence in a Track as an arrow.
    """
    arrow = ' -({n})-> '
    return str(occ.state_name), arrow.format(n=len(occ.transitions)+1)

class StateOccurrence:
    """
    A state in the context of the transition sequence.

    If the state machine execution looks like

        (state 1) -> (state 2) -> (state 1)

    then there are two occurrences of (state 1) and one of (state 2).
    """
    def __init__(self, state):
        self.state = state
        self.transitions = []

    def set_transitions(self, transitions):
        """
        Set the list of transitions for this occurrence.
        """
        self.transitions = transitions

    def remove_transition(self, transition):
        """
        Remove one transition from the occurrence's transition list.
        """
        self.transitions.remove(transition)


class Track:
    """
    Sequence of states visited by the state machine.

    This is a stack of StateOccurrence objects, with a bound on its depth.
    """
    def __init__(self, max_occ=-1):
        self.occurrences = []
        self.max_occ = max_occ

    def append(self, occ):
        """
        Append an occurrence to this track.
        """
        self.occurrences.append(occ)
        if self.max_occ < 0:
            return
        track_len = len(self.occurrences)
        if track_len > self.max_occ:
            del self.occurrences[0:track_len - self.max_occ]

    def last(self):
        """
        Return the last occurrence in a Track.
        """
        return self.occurrences[-1]

    def __iter__(self):
        return self.occurrences.__iter__()

    def __str__(self):
        if len(self.occurrences) == 0:
            return '<Empty Track>'

        formatter = map(_track_format, self.occurrences)
        chainer = itertools.chain.from_iterable(formatter)

        return ''.join(itertools.islice(chainer, 2*len(self.occurrences) - 1))

class Backtracking:
    """
    Mix-in to implement backtracking in a state machine.
    """
    def __init__(self, max_occ=-1, **kw_args):
        super().__init__(**kw_args)
        self.track = Track(max_occ)

        if __debug__:
            if type(self).mro().index(Backtracking) > \
                    type(self).mro().index(StateMachine):
                raise AssertionError("class Backtracking modifies class " \
                                     "StateMachine and must be ahead of it " \
                                     "in the mro.")

    def on_enter_state(self, s_name):
        """
        Handle on_enter notifications for backtracking.
        """
        self.track.append(self.make_occurrence())
        super().on_enter_state(s_name)

    def make_occurrence(self):
        """
        Create an occurrence from the current state.

        Allows Backtracking derived classes to use their own occurrence data.
        """
        return StateOccurrence(self.current_state)

    def _backtrack(self):
        """
        Backtrack, reentering the state after the most recent unexplored
        transition.

        Returns:
            True if an alternate path was found, False is all paths are
            exhausted.
        """

        super()._exit()
        # Find the latest occurrence that doesn't have an empty transition
        # stack.
        for occ in reversed(self.track.occurrences):
            if len(occ.transitions) > 0:
                self.current_state = occ.state

                super()._transition_multiple(occ.transitions)

                return True
            else:
                self.current_state = occ.state
                self.on_backtrack(occ)
                self.track.occurrences.pop()

        return False

    def on_transition(self, exiting, entering):
        """
        Notification that a transition is in effect.
        """
        occ = self.track.last()
        occ.remove_transition(entering)

        super().on_transition(exiting, entering)

    def on_no_transition(self, s_name):
        if self._backtrack():
            return
        else:
            self.on_exhausted()

            raise Reject("Backtracking exhausted.")

    def on_exhausted(self):
        """
        Backtracking is exhausted notification handler.

        The specified StateOccurrence has been backtracked, and is about to be
        deleted.  This provides a chance to synchronize application data.

        If you overload this method, be sure to call super().on_exhausted().
        """
        pass

    def on_backtrack(self, occ):
        """
        Backtrack notification handler.

        The specified StateOccurrence has been backtracked, and is about to be
        deleted.  This provides a chance to synchronize application data.

        If you overload this method, be sure to call super().on_backtrack().
        """
        pass

    def on_pre_select_transition(self, s_name, allowed_transitions):
        """
        Handle pre_select_transition notifications.

        Captures the allowed transitions for backtracking.
        """
        occ = self.track.last()
        occ.set_transitions(allowed_transitions)

        super().on_pre_select_transition(s_name, allowed_transitions)

if __name__ == '__main__':
    import sys
    sys.stderr.write("Pycog backtrack.py module is not intended to run "
                     "standalone.")

