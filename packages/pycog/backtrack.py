"""Support for back-tracking in state machines"""

import itertools

_arrow = ' -({n})-> '
def _track_format(occ):
    return str(occ.state_name), _arrow.format(n=len(occ.transitions)+1)

class StateOccurrence:
    """
    A state in the context of the transition sequence.

    If the state machine execution looks like

        (state 1) -> (state 2) -> (state 1)

    then there are two occurrences of (state 1) and one of (state 2).
    """
    def __init__(self, state_name):
        self.state_name = state_name
        self.transitions = []

    def set_transitions(self, transitions):
        self.transitions = transitions

    def remove_transition(self, transition):
        self.transitions.remove(transition)

class Track:
    """
    Sequence of StateOccurrence instances representing the sequence of states
    visited by the state machine.
    """
    def __init__(self, max_occ = -1):
        self.occurrences = []
        self.max_occ = max_occ

    def append(self, occ):
        self.occurrences.append(occ)
        if self.max_occ < 0:
            return
        l = len(self.occurrences)
        if l > self.max_occ:
            del self.occurrences[0:l - self.max_occ]

    def last(self):
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
    """Mix-in to implement backtracking in a state machine."""
    def __init__(self, max_occ = -1):
        self.track = Track(max_occ)

    def _bt_on_enter_state(self):
        self.track.append(self.make_occurrence())

    def make_occurrence(self):
        """
        Create an occurrence from the current state.  Allows Backtracking
        derived classes to use their own occurrence data.
        """
        return StateOccurrence(self.state_name)

    def _backtrack(self):
        """
        Backtrack, reentering the state after the most recent unexplored
        transition.

        Returns True if an alternate path was found, False is all paths are
        exhausted.
        """

        self.exit()
        # Find the latest occurrence that doesn't have an empty transition
        # stack.
        for occ in reversed(self.track.occurrences):
            if len(occ.transitions) > 0:
                self.state_name = occ.state_name

                next_state = self._bt_select_transition(occ.transitions)
                self.on_transition(next_state)

                self.state_name = next_state
                self.enter()

                return True
            else:
                self.state_name = occ.state_name
                self.on_backtrack(occ)
                self.track.occurrences.pop()

        return False

    def on_backtrack(self, occ):
        """
        Notification that the specified StateOccurrence has been backtracked,
        and is about to be deleted.  This provides a chance to synchronize
        application data.
        """
        pass

    def _bt_select_transition(self, allowed_transitions):
        """
        Captures the allowed transitions, and delegates to select_transition()
        to choose among them.  Because state_machine calls this instead of
        select_transitions directly (if _bt_select_transition is present),
        overloading select_transitions() does not require a super-message to
        Backtracking.
        """
        occ = self.track.last()
        occ.set_transitions(allowed_transitions)

        trans = self.select_transition(allowed_transitions)
        occ.remove_transition(trans)

        return trans

if __name__ == '__main__':

    from statemachine import *
    from exceptions import *

    class MinimalChange(StateMachine, Backtracking):
        def __init__(self, amount, coin_values):
            StateMachine.__init__(self, 'init')
            Backtracking.__init__(self)
            self.amount = amount

            def transition_test(value):
                def _transition_test(self):
                    nonlocal value
                    return value <= self.amount - self.accumulated
                return _transition_test

            def done_test(self):
                return self.amount == self.accumulated

            self.coins = dict()
            last_state = self.final
            for value in sorted(coin_values):
                coin_state = State(value, MinimalChange.in_coin_state)
                coin_state.value = value
                self.add_state(coin_state)
                self.coins[value] = coin_state

                coin_state.add_transition('final', done_test)
                coin_state.add_transition(value, transition_test(value))
                coin_state.copy_transitions(last_state)

                last_state = coin_state

            self.init.copy_transitions(last_state)

        def in_coin_state(self):
            self.num_coins += 1
            self.accumulated += self.state.value
            if self.num_coins == self.fewest:
                raise Backtrack()

        @state('init')
        def init(self):
            self.accumulated = 0
            self.fewest = self.amount
            self.num_coins = 0
            self.first_run = True
            self.greedy = 0

        @state('final')
        def final(self):
            # print(self.num_coins, 'coins:', self.track)
            if self.num_coins < self.fewest:
                self.fewest = self.num_coins

            if self.first_run:
                self.greedy = self.num_coins
                self.first_run = False

            raise Backtrack()

        def on_backtrack(self, occ):
            if occ.state_name not in ['init', 'final']:
                self.accumulated -= self.state.value
                self.num_coins -= 1
            # print('Backtracking:', self.track)

        def on_exhausted(self):
            pass

    fsm = MinimalChange(35, [1, 3, 5, 7, 11, 13])
    fsm.run()

    print('Amount:', 35, 'Greedy:', fsm.greedy, 'Best:', fsm.fewest)

