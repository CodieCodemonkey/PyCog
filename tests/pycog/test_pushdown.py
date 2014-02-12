"""Test pycog.pushdown"""

import sys
import os.path as op

# Need this so we pick up the code base for which this is a test, not an
# installed version.
package_dir = op.abspath(op.join('..', 'packages'))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

example_dir = op.abspath(op.join('..', 'examples'))
if example_dir not in sys.path:
    sys.path.insert(0, example_dir)

import unittest
from io import StringIO

from check_parens import ParenChecker

class CheckParensTest(unittest.TestCase):
    def test_1(self):
        test = ParenChecker(StringIO("( )"))
        self.assertTrue(test.run())

    def test_2(self):
        test = ParenChecker(StringIO("("))
        self.assertFalse(test.run())

    def test_3(self):
        test = ParenChecker(StringIO(")"))
        self.assertFalse(test.run())

    def test_4(self):
        test = ParenChecker(StringIO("(()"))
        self.assertFalse(test.run())

    def test_5(self):
        test = ParenChecker(StringIO("())"))
        self.assertFalse(test.run())

    def test_6(self):
        test = ParenChecker(StringIO("(([] {}) ())"))
        self.assertTrue(test.run())

    def test_7(self):
        test = ParenChecker(StringIO("(([] {} ())"))
        self.assertFalse(test.run())

    def test_8(self):
        test = ParenChecker(StringIO("(([] { ())"))
        self.assertFalse(test.run())

    def test_9(self):
        test = ParenChecker(StringIO("(([] { () })"))
        self.assertFalse(test.run())

