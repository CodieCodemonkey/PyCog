"""Test pycog.graph"""

import sys

# Need this so we pick up the code base for which this is a test, not an
# installed version.
sys.path.append("../packages")

import unittest

from pycog.graph import Graph, GraphWrapper

class TestGraph(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()

    def test_vertices(self):
        """Test adding and removing vertices"""

        self.assertEqual(self.graph.num_vertices(), 0)

        self.graph.add("a")
        self.graph.add("b")
        self.graph.add("c")
        self.graph.add("d")
        self.graph.add("e")

        self.assertEqual(self.graph.num_vertices(), 5)

        self.graph.remove("b")
        self.graph.remove("e")
        self.assertEqual(self.graph.num_vertices(), 3)

        self.graph.clear()
        self.assertEqual(self.graph.num_vertices(), 0)

    def test_connect(self):
        for i in range(10): self.graph.add(i)

        # Connect each integer to its successors in the graph
        for v in range(9):
            for s in range(v+1, 10):
                self.graph.connect(v, s)

        # Test degree
        for v in range(10):
            self.assertEqual(self.graph.in_degree(v), v)
            self.assertEqual(self.graph.out_degree(v), 9-v)

        # Test succ
        for v in range(10):
            expected = set(range(v + 1, 10))
            for s in self.graph.succ(v):
                expected.remove(s)
            self.assertEqual(len(expected), 0)

        # Test pred
        for v in range(10):
            expected = set(range(v))
            for s in self.graph.pred(v):
                expected.remove(s)
            self.assertEqual(len(expected), 0)

class TestGraphWrapper(TestGraph):
    def setUp(self):
        self.graph = GraphWrapper(Graph())

class MinGraph:
    """
    Graph class with only required protcol methods.
    """

    def __init__(self):
        self._vertices = set()
        self._succ = dict()

    def vertices(self):
        """Return an iterator over the vertices."""

        return self._vertices.__iter__()

    def succ(self, v):
        """
        Get the successors of a vertex.

        Args:
            v: Vertex for which successors are desired.

        Returns:
            An iterator over the successor vertices.

        Raises:
            KeyError if the vertex is not in the graph.
        """
        return self._succ[v].__iter__()

    def add(self, v):
        """
        Add a vertex to the graph.

        Args:
            v: Vertex to add.
        """
        self._vertices.add(v)
        self._succ[v] = set()

    def remove(self, v):
        """
        Remove a vertex from the graph.

        Args:
            v: Vertex to remove.
        """
        for s in self.succ(v):
            self.disconnect(v, s)
        self._vertices.remove(v)
        del self._succ[v]

    def connect(self, pred, succ):
        """
        Create a directed edge between two vertices.

        Args:
            pred: predecessor vertex.  The edge is traversed from this vertex.
            succ: successor vertex.  The edge is traversed to this vertex.

        Raises:
            KeyError if either vertex is not in the graph.
        """
        self._succ[pred].add(succ)

    def disconnect(self, pred, succ):
        """
        Removed a directed edge between two vertices.

        Args:
            pred: predecessor vertex.  The edge is traversed from this vertex.
            succ: successor vertex.  The edge is traversed to this vertex.

        Raises:
            KeyError if either vertex is not in the graph.
        """
        self._succ[pred].remove(succ)

    #
    # Graph protocol definitions
    #

    # Required
    gp_vertices = vertices
    gp_succ = succ
    gp_add = add
    gp_remove = remove
    gp_connect = connect
    gp_disconnect = disconnect

class TestGraphWrapperMin(TestGraph):
    def setUp(self):
        self.graph = GraphWrapper(MinGraph())

if __name__ == '__main__':
    unittest.main()

