"""Test pycog.graph"""

import sys

# Need this so we pick up the code base for which this is a test, not an
# installed version.
sys.path.append("../packages")

import unittest

from pycog.graph import graph

class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = graph()

    def test_create(self):
        """Test adding of vertices and connecting them."""

        self.assertEqual(self.graph.num_vertices(), 0)

        self.graph.add_vertex("a")
        self.graph.add_vertex("b")
        self.graph.add_vertex("c")
        self.graph.add_vertex("d")
        self.graph.add_vertex("e")

        self.assertEqual(self.graph.num_vertices(), 5)

if __name__ == '__main__':
    unittest.main()

