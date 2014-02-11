"""Minimum change problem -- backtracking example."""

if __name__ == "__main__":
    import sys
    import os.path as op
    sys.path.append(op.abspath(op.join('..', 'packages')))

from pycog.exceptions import *
from pycog.statemachine import *
from pycog.backtrack import *

class MinimalChange(StateMachine, Backtracking):
    def __init__(self, amount, coin_values):
        super().__init__(initial='init')

        self.amount = amount
        self.accumulated = 0
        self.fewest = self.amount
        self.num_coins = 0
        self.first_run = True
        self.greedy = 0
        self.coins = {}
        self.best_coins = {}

        def transition_test(value):
            def _transition_test(self, current_state, next_state):
                nonlocal value
                return value <= self.amount - self.accumulated
            return _transition_test

        def done_test(self, current_state, next_state):
            return self.amount == self.accumulated

        # Create a state for each coin denomination
        values = []
        for value in sorted(coin_values, reverse=True):
            self.coins[value] = 0
            values.append(value)
            self.add_state(value, activity=MinimalChange.in_coin_state)

        # Init can transition to any coin state
        self.add_transition('init', 'final', done_test)
        for value in values:
            self.add_transition('init', value, transition_test(value))

        # Lower denominations can transition to higher ones
        while len(values) > 0:
            next_value = values[-1]
            self.add_transition(next_value, 'final', done_test)
            for value in values:
                self.add_transition(value, next_value,
                                    transition_test(next_value))
            values.pop()

    def in_coin_state(self):
        self.num_coins += 1
        self.coins[self.current_state] += 1
        self.accumulated += self.current_state

        # Short-circuit if we already have a solution with this many coins
        if self.num_coins == self.fewest:
            raise Backtrack()

    @state('init')
    def init(self):
        pass

    @state('final')
    def final(self):
        if self.num_coins < self.fewest:
            self.fewest = self.num_coins
            self.best_coins = dict((k,v) for (k,v) in self.coins.items())

        if self.first_run:
            self.greedy = self.num_coins
            self.first_run = False

        raise Backtrack()

    def on_backtrack(self, occ):
        if occ.state not in ['init', 'final']:
            # This works because coin states are integers
            self.accumulated -= self.current_state
            self.num_coins -= 1
            self.coins[self.current_state] -= 1

    def on_exhausted(self):
        pass

if __name__ == "__main__":
    fsm = MinimalChange(35, [1, 3, 5, 7, 11, 13])
    fsm.run()

    print('Amount:', 35, 'Greedy:', fsm.greedy, 'Best:', fsm.fewest)
    print(fsm.best_coins)

