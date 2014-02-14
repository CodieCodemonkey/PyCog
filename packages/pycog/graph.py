"""Graph implementation."""

class Graph:
    """
    Basic graph class.

    This is an implemenation of the graph protocol defined at
    http://pycog.codiecodemonkey.com/graph-protocol.html.
    """

    def __init__(self, **kw_args):
        super().__init__(**kw_args)

        self._vertices = set()
        self._pred = dict()
        self._succ = dict()

    def vertices(self):
        """Return an iterator over the vertices."""

        return self._vertices.__iter__()

    def succ(self, vertex):
        """
        Get the successors of a vertex.

        Args:
            vertex: Vertex for which successors are desired.

        Returns:
            An iterator over the successor vertices.

        Raises:
            KeyError
        """
        return self._succ[vertex].__iter__()

    def pred(self, vertex):
        """
        Get the predecessors of a vertex.

        Args:
            vertex: Vertex for which predecessors are desired.

        Returns:
            An iterator over the preceding vertices.

        Raises:
            KeyError
        """
        return self._pred[vertex].__iter__()

    def add(self, vertex):
        """
        Add a vertex to the graph.

        Args:
            vertex: Vertex to add.
        """
        self._vertices.add(vertex)
        self._pred[vertex] = set()
        self._succ[vertex] = set()

    def remove(self, vertex):
        """
        Remove a vertex from the graph.

        Args:
            vertex: Vertex to remove.
        """
        for pred in self.pred(vertex):
            self.disconnect(pred, vertex)
        for succ in self.succ(vertex):
            self.disconnect(vertex, succ)
        self._vertices.remove(vertex)
        del self._pred[vertex]
        del self._succ[vertex]

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
            KeyError
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
            KeyError
        """
        self._succ[pred].remove(succ)
        self._pred[succ].remove(pred)

    def in_degree(self, vertex):
        """
        Get the in-degree of a vertex.

        The "in-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            vertex: Query vertex.

        Returns:
            The number of incoming edges as an integer.

        Raises:
            KeyError
        """
        return len(self._pred[vertex])

    def out_degree(self, vertex):
        """
        Get the out-degree of a vertex.

        The "out-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            vertex: Query vertex.

        Returns:
            The number of outgoing edges as an integer.

        Raises:
            KeyError
        """
        return len(self._succ[vertex])

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

    def succ(self, vertex):
        """
        Get the successors of a vertex.

        Args:
            vertex: Vertex for which successors are desired.

        Returns:
            An iterator over the successor vertices.

        Raises:
            KeyError
        """
        return self._graph.gp_succ(vertex)

    def pred(self, vertex):
        """
        Get the predecessors of a vertex.

        Args:
            vertex: Vertex for which predecessors are desired.

        Returns:
            An iterator over the preceding vertices.

        Raises:
            KeyError
        """
        def pred_gen(vertex):
            """Brute force generation of predecessors."""
            for vert in self.vertices():
                for succ in self.succ(vert):
                    if succ == vertex:
                        yield vert

        if hasattr(self._graph, 'gp_pred'):
            return self._graph.gp_pred(vertex)
        else:
            return pred_gen(vertex)

    def add(self, vertex):
        """
        Add a vertex to the graph.

        Args:
            vertex: Vertex to add.
        """
        return self._graph.gp_add(vertex)

    def remove(self, vertex):
        """
        Remove a vertex from the graph.

        Args:
            vertex: Vertex to remove.
        """
        return self._graph.gp_remove(vertex)

    def clear(self):
        """Remove all vertices."""
        if hasattr(self._graph, 'gp_clear'):
            self._graph.gp_clear()
        else:
            verts = [vertex for vertex in self._graph.vertices()]
            for vertex in verts:
                self._graph.remove(vertex)

    def connect(self, pred, succ):
        """
        Create a directed edge between two vertices.

        Args:
            pred: predecessor vertex.  The edge is traversed from this vertex.
            succ: successor vertex.  The edge is traversed to this vertex.

        Raises:
            KeyError
        """
        return self._graph.gp_connect(pred, succ)

    def disconnect(self, pred, succ):
        """
        Removed a directed edge between two vertices.

        Args:
            pred: predecessor vertex.  The edge is traversed from this vertex.
            succ: successor vertex.  The edge is traversed to this vertex.

        Raises:
            KeyError
        """
        return self._graph.gp_disconnect(pred, succ)

    def in_degree(self, vertex):
        """
        Get the in-degree of a vertex.

        The "in-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            vertex: Query vertex.

        Returns:
            The number of incoming edges as an integer.

        Raises:
            KeyError
        """
        if hasattr(self._graph, 'gp_in_degree'):
            return self._graph.gp_in_degree(vertex)
        else:
            cnt = -1
            for cnt, _ in enumerate(self.pred(vertex)):
                pass
            return cnt + 1

    def out_degree(self, vertex):
        """
        Get the out-degree of a vertex.

        The "out-degree" is defined as the number of edges coming into the
        vertex.

        Args:
            vertex: Query vertex.

        Returns:
            The number of outgoing edges as an integer.

        Raises:
            KeyError
        """
        if hasattr(self._graph, 'gp_out_degree'):
            return self._graph.gp_out_degree(vertex)
        else:
            cnt = -1
            for cnt, _ in enumerate(self.succ(vertex)):
                pass
            return cnt + 1

    def num_vertices(self):
        """Number of vertices in the graph."""
        if hasattr(self._graph, 'gp_out_degree'):
            return self._graph.gp_num_vertices()
        else:
            cnt = -1
            for cnt, _ in enumerate(self.vertices()):
                pass
            return cnt + 1

