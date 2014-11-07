"""Backtracking example: 8-queens problem."""

if __name__ == "__main__":
    import sys
    import os.path as op
    sys.path.append(op.abspath(op.join('..', 'packages')))

from pycog.statemachine import *
from pycog.exceptions import *
from pycog.backtrack import *
from pycog.utility.diagram import diagram

# Strategy:
#
# The states are ordered pairs (row, col) for each of the 64 squares on the
# board.  The state has two possible values: False if there is no queen on the
# square, True otherwise.  When we enter a state we record the coordinates of
# the associated square as a queen location.  When we backtrack we erase that
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

def transition_test(fsm, cur_square, next_square):
    """
    Transition test

    Check that the next square doesn't violate the "no queen attacking" rule by
    looking at the rows and diagonals.  The transition strategy (see
    EightQueens) makes checking columns unnecessary.
    """
    next_row, next_col = next_square

    # check the row
    for col in range(next_col):
        if (next_row, col) in fsm.queens:
            return False

    # check the two diagonals so far, from (next_row, next_col)
    diag_len = min(next_row, next_col)
    for step in range(diag_len):
        if (next_row - step - 1, next_col - step - 1) in fsm.queens:
            return False

    diag_len = min(7 - next_row, next_col)
    for step in range(diag_len):
        if (next_row + step + 1, next_col - step - 1) in fsm.queens:
            return False

    return True

class EightQueens(Backtracking, StateMachine):
    """
    Solve the 8-queens problem using backtracking.

    State Strategy:
        The state names are 'init', 'final' and the coordinates (row, col) on
        the chessboard.  There is no state data, the names contain all the
        information we need.

    Transition Strategy:
        'init' transitions to the first 4 rows of column 0.  We don't bother
        transitioning to the last 4 rows because by symmetry if there is a
        solution with a queen in the last 4 squares of the first column, then
        one can flip the board to get a solution in the first 4 rows.

        Each square in any given column transitions to all the squares of the
        next column, except for the squares on the same row or diagonal.

        All squares of the last column transition to 'final'.

    Attributes:
        queens: Set of (row, col) coordinates, each being the position of one
            of the eight queens.
    """

    def __init__(self):
        super().__init__(initial='init')

        self.queens = set()

        # Add states for each square
        for row in range(8):
            for col in range(8):
                self.add_state((row, col), activity=EightQueens.place_queen)

        # Add transitions
        for row in range(8):
            # Transitions from 'init' and to 'final'.
            if row < 4: self.add_transition('init', (row, 0))
            self.add_transition((row, 7), 'final')

            for col in range(7):
                for next_row in range(8):
                    # Short circuit impossible transitions
                    if next_row == row: continue
                    if next_row == row + 1: continue
                    if next_row == row - 1: continue

                    self.add_transition((row, col), (next_row, col + 1),
                                         transition_test)

    def place_queen(self):
        """In a square state, meaning we place a queen on this square."""
        self.queens.add(self.current_state)

    @state("init")
    def init(self):
        """
        Starting state for our search.

        This state is needed so that we have something to backtrack to in order
        to choose a different first column queen.  It isn't absolutely
        necessary since we know there is a solution with a queen in the first
        row of the first column.
        """
        pass

    @state("final", accepting=True)
    def final(self):
        """A solution is found, draw the board."""
        raise Accept()

    def draw(self):
        """Draw the board as text."""
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
        super().on_backtrack(occ)

        # Uncomment these two lines to display the state of the board each time
        # backtracking occurs.
        # print()
        # self.draw()

        if occ.state not in ['init', 'final']:
            self.queens.remove(self.current_state)

    def on_exhausted(self):
        """
        Handle the case where no solution can be found.

        This should never happen.
        """
        raise Exception("No solution found!")

if __name__ == "__main__":
    solver = EightQueens()
    solver.run()
    solver.draw()

    with open("eight_queens.gv", "w") as gv_file:
        diagram(solver, gv_file)

