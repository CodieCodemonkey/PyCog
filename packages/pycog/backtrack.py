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

    def _bt_on_enter_state(self):
        """
        Handle on_enter notifications for backtracking.

        This should be removed in favor of super-messaging.
        """
        self.track.append(self.make_occurrence())

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

        self._exit()
        # Find the latest occurrence that doesn't have an empty transition
        # stack.
        for occ in reversed(self.track.occurrences):
            if len(occ.transitions) > 0:
                self.current_state = occ.state

                next_state = self._bt_select_transition(occ.transitions)
                self.on_transition(self.current_state, next_state)

                self.current_state = next_state
                self._enter()

                return True
            else:
                self.current_state = occ.state
                self.on_backtrack(occ)
                self.track.occurrences.pop()

        return False

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

    def _bt_select_transition(self, allowed_transitions):
        """
        Backtracking select transition hook.

        Captures the allowed transitions, and delegates to select_transition()
        to choose among them.

        Because state_machine calls this instead of select_transitions directly
        (if _bt_select_transition is present), overloading select_transitions()
        does not require a super-message to Backtracking.
        """
        occ = self.track.last()
        occ.set_transitions(allowed_transitions)

        trans = self.select_transition(self.current_state, allowed_transitions)
        occ.remove_transition(trans)

        return trans

if __name__ == '__main__':
    import sys
    sys.stderr.write("Pycog backtrack.py module is not intended to run "
                     "standalone.")

