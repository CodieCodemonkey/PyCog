"""Backtracking example: 8-queens problem."""

import sys
sys.path.append("../packages/")

from pycog.statemachine import *
from pycog.exceptions import *
from pycog.backtrack import *

# Strategy:
#
# The states are ordered pairs (row, col) for each of the 64 squares on the
# board.  The state has two possible values: False if there is no queen on the
# square, True otherwise.  When we enter a state we record the coordinates of
# the assocated square as a queen location.  When we backtrack we erase that
# record.
#
# We could allow a transition from any square to any other one, but we'll use
# the transitions we assign to each square limit the paths.  For any square
# (row, col) we'll only consider transitions into the squares of the next
# column, that are not in the same row.  So there are 7 candidate transitions
# from any square, except for the ones in the last column, which all transition
# to state "final".
#
# The transition tests will allow check for queen on the same diagonal or row
# as the candidate square.  There is no need to check for a queen in the same
# column because the choice of transitions precludes that possibility.

def transition_test(next_square):
    """Create a transition test for square (next_row, next_col)"""

    def _transition_test(self):
        nonlocal next_square

        next_row, next_col = next_square

        # check the row
        for col in range(next_col):
            if (next_row, col) in self.queens:
                return False

        # check the two diagonals so far, from (next_row, next_col)
        diag_len = min(next_row, next_col)
        for step in range(diag_len):
            if (next_row - step - 1, next_col - step - 1) in self.queens:
                return False

        diag_len = min(7 - next_row, next_col)
        for step in range(diag_len):
            if (next_row + step + 1, next_col - step - 1) in self.queens:
                return False

        return True
    return _transition_test

class EightQueens(StateMachine, Backtracking):
    """
    Solve the 8-queens problem using backtracking.
    """

    def __init__(self):
        StateMachine.__init__(self, 'init')
        Backtracking.__init__(self)

        self.queens = set()

        init_state = self.get_state_from_name('init')

        # Add states for each square
        for row in range(8):
            for col in range(8):
                state = State((row, col), EightQueens.place_queen)
                self.add_state(state)

                # Add transitions to the next column
                for next_row in range(8):
                    if row == next_row: continue
                    state.add_transition((next_row, col + 1),
                                         transition_test((next_row, col + 1)))

                # "init" transitions to the squares of the first column
                if col == 0:
                    init_state.add_transition((row, col), lambda self: True)

                # The squares in the last column transition to final
                if col == 7:
                    state.add_transition('final', lambda self: True)

    def place_queen(self):
        """In a square state, meaning we place a queen on this square."""
        self.queens.add(self.state_name)
        self.draw()

    @state("init")
    def init(self): pass

    @state("final")
    def final(self):
        """A solution is found, draw the board."""
        self.draw()
        raise Accept()

    def draw(self):
        sys.stdout.write('\n')
        for row in range(8):
            for col in range(8):
                if (row, col) in self.queens:
                    sys.stdout.write(' Q ')
                else:
                    sys.stdout.write(' . ')
            sys.stdout.write('\n')

    def on_backtrack(self, occ):
        """Undo the placing of a queen in response to backtracking."""
        if occ.state_name not in ['init', 'final']:
            self.queens.remove(self.state_name)

    def on_exhausted(self):
        print("No solution found!")

solver = EightQueens()
solver.run()

