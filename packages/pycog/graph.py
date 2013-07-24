"""Graph implementation."""

class Graph:
    """
    Basic graph class.

    This is an implemenation of the graph protocol defined at
    http://pycog.codiecodemonkey.com/graph-protocol.html.
    """

    def __init__(self):
        self._vertices = set()
        self._pred = dict()
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

    def pred(self, v):
        """
        Get the predecessors of a vertex.

        Args:
            v: Vertex for which predecessors are desired.

        Returns:
            An iterator over the preceding vertices.

        Raises:
            KeyError if the vertex is not in the graph.
        """
        return self._pred[v].__iter__()

    def add(self, v):
        """
        Add a vertex to the graph.

        Args:
            v: Vertex to add.
        """
        self._vertices.add(v)
        self._pred[v] = set()
        self._succ[v] = set()

    def remove(self, v):
        """
        Remove a vertex from the graph.

        Args:
            v: Vertex to remove.
        """
        for p in self.pred(v):
            self.disconnect(p, v)
        for s in self.succ(v):
            self.disconnect(v, s)
        self._vertices.remove(v)
        del self._pred[v]
        del self._succ[v]

    def clear(self):
        """Remove all vertices."""
        self._vertices.clear()
        self._pred.clear()
        self._succ.clear()

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
        self._pred[succ].add(pred)

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
        self._pred[succ].remove(pred)

    def in_degree(self, v):
        """
        Get the in-degree of a vertex.

        The "in-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            v: Query vertex.

        Returns:
            The number of incoming edges as an integer.

        Raises:
            KeyError
        """
        return len(self._pred[v])

    def out_degree(self, v):
        """
        Get the out-degree of a vertex.

        The "out-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            v: Query vertex.

        Returns:
            The number of outgoing edges as an integer.

        Raises:
            KeyError
        """
        return len(self._succ[v])

    def num_vertices(self):
        """Number of vertices in the graph."""
        return len(self._vertices)

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

    # Recommended
    gp_pred = pred

    # Optional
    gp_clear = clear
    gp_in_degree = in_degree
    gp_out_degree = out_degree
    gp_num_vertices = num_vertices


class GraphWrapper:
    """
    Wrapper for classes implementing the graph protocol.

    The input instance must have the required methods of defined by the graph
    protocol.  Any optional methods from the input class are used when
    available, otherwise implementations are provided in the wrapper.
    """

    def __init__(self, graph):
        self._graph = graph

    def vertices(self):
        """Return an iterator over the vertices."""

        return self._graph.gp_vertices()

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
        return self._graph.gp_succ(v)

    def pred(self, v):
        """
        Get the predecessors of a vertex.

        Args:
            v: Vertex for which predecessors are desired.

        Returns:
            An iterator over the preceding vertices.

        Raises:
            KeyError if the vertex is not in the graph.
        """
        def pred_gen(v):
            """Brute force generation of predecessors."""
            for vert in self.vertices():
                for s in self.succ(vert):
                    if s == v:
                        yield vert

        if hasattr(self._graph, 'gp_pred'):
            return self._graph.gp_pred(v)
        else:
            return pred_gen(v)

    def add(self, v):
        """
        Add a vertex to the graph.

        Args:
            v: Vertex to add.
        """
        return self._graph.gp_add(v)

    def remove(self, v):
        """
        Remove a vertex from the graph.

        Args:
            v: Vertex to remove.
        """
        return self._graph.gp_remove(v)

    def clear(self):
        """Remove all vertices."""
        if hasattr(self._graph, 'gp_clear'):
            self._graph.gp_clear()
        else:
            verts = [v for v in self._graph.vertices()]
            for v in verts:
                self._graph.remove(v)

    def connect(self, pred, succ):
        """
        Create a directed edge between two vertices.

        Args:
            pred: predecessor vertex.  The edge is traversed from this vertex.
            succ: successor vertex.  The edge is traversed to this vertex.

        Raises:
            KeyError if either vertex is not in the graph.
        """
        return self._graph.gp_connect(pred, succ)

    def disconnect(self, pred, succ):
        """
        Removed a directed edge between two vertices.

        Args:
            pred: predecessor vertex.  The edge is traversed from this vertex.
            succ: successor vertex.  The edge is traversed to this vertex.

        Raises:
            KeyError if either vertex is not in the graph.
        """
        return self._graph.gp_disconnect(pred, succ)

    def in_degree(self, v):
        """
        Get the in-degree of a vertex.

        The "in-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            v: Query vertex.

        Returns:
            The number of incoming edges as an integer.

        Raises:
            KeyError
        """
        if hasattr(self._graph, 'gp_in_degree'):
            return self._graph.gp_in_degree(v)
        else:
            cnt = -1
            for cnt, _ in enumerate(self.pred(v)): pass
            return cnt + 1

    def out_degree(self, v):
        """
        Get the out-degree of a vertex.

        The "out-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            v: Query vertex.

        Returns:
            The number of outgoing edges as an integer.

        Raises:
            KeyError
        """
        if hasattr(self._graph, 'gp_out_degree'):
            return self._graph.gp_out_degree(v)
        else:
            cnt = -1
            for cnt, _ in enumerate(self.succ(v)): pass
            return cnt + 1

    def num_vertices(self):
        """Number of vertices in the graph."""
        if hasattr(self._graph, 'gp_out_degree'):
            return self._graph.gp_num_vertices()
        else:
            cnt = -1
            for cnt, _ in enumerate(self.vertices()): pass
            return cnt + 1
