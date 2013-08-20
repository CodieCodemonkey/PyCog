"""Test pycog.statemachine"""

import sys

# Need this so we pick up the code base for which this is a test, not an
# installed version.
sys.path.append("../packages")
sys.path.append("../examples")

import unittest
from io import StringIO

import eight_queens
from ps_and_qs import PsAndQs
from min_change import MinimalChange

class EightQueensTest(unittest.TestCase):
    def test_eightqueens(self):
        solver = eight_queens.EightQueens()
        solver.run()

class PsAndQsTest(unittest.TestCase):
    def test_pppqqqqq(self):
        test = PsAndQs(StringIO("pppqqqqq"))
        self.assertTrue(test.run())

    def test_qqqqpppp(self):
        test = PsAndQs(StringIO("qqqqpppp"))
        self.assertFalse(test.run())

    def test_rppppqqqq(self):
        test = PsAndQs(StringIO("rppppqqqq"))
        self.assertFalse(test.run())

    def test_pppprqqqq(self):
        test = PsAndQs(StringIO("pppprqqqq"))
        self.assertFalse(test.run())

    def test_ppppqqqqr(self):
        test = PsAndQs(StringIO("ppppqqqqr"))
        self.assertFalse(test.run())

    def test_qqqqqqq(self):
        test = PsAndQs(StringIO("qqqqqqq"))
        self.assertTrue(test.run())

    def test_pppppp(self):
        test = PsAndQs(StringIO("pppppp"))
        self.assertTrue(test.run())

class MinChange(unittest.TestCase):
    def test_min_change(self):
        fsm = MinimalChange(35, [1, 3, 5, 7, 11, 13])
        fsm.run()
        self.assertEqual(fsm.fewest, 3)

