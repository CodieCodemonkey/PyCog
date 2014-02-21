"""Graph implementation."""

class Graph:
    """
    Basic graph class.

    This is an implementation of the graph protocol defined at
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
        if hasattr(self._graph, 'gp_num_vertices'):
            return self._graph.gp_num_vertices()
        else:
            cnt = -1
            for cnt, _ in enumerate(self.vertices()):
                pass
            return cnt + 1

class BreadthFirstSearch:
    """
    Implements the breadth-first search algorithm.
    """
    def __init__(self, graph, start_vertex, visit_callback = None):
        if type(graph) is GraphWrapper:
            self.graph = graph
        else:
            self.graph = GraphWrapper(graph)
        self.root = start_vertex
        self.visited = None
        self.visit_callback = visit_callback

    def run(self):
        """
        Do the search.
        """
        # Clear state from any previous run.
        self.visited = set()

        self.visited.add(self.root)
        self.on_visit(self.root)
        current_rank = set()
        current_rank.add(self.root)
        while current_rank:
            self.on_rank_acquired(current_rank)
            next_rank = set()

            for vert in current_rank:
                if vert == None:
                    import pudb;pudb.set_trace()
                for succ_vert in self.graph.succ(vert):
                    if succ_vert not in self.visited:
                        self.visited.add(succ_vert)
                        self.on_visit(succ_vert)
                        next_rank.add(succ_vert)

            current_rank = next_rank

    def on_visit(self, vertex):
        """
        Handle notification that a vertex has been visited.

        Args:
            vertex: The visited vertex.

        Returns:
            True if the search should continue, False otherwise.

        Any overload of this function must call super().on_visit().
        """
        if self.visit_callback:
            return self.visit_callback(vertex)

        return True

    def on_rank_acquired(self, rank):
        """
        Handle notification that a rank has been acquired.

        Args;
            rank: set of vertices in the rank.

        Any overload of this function must call super().on_rank_acquired().
        """
        pass

def is_tree(graph):
    """
    Determine if a directed graph is a (rooted) tree and find its root.

    Args:
        graph: graph to check, must satisfy the graph protocol.

    Returns:
        None if the graph is not a tree, otherwise the root vertex.
    """
    if type(graph) is not GraphWrapper:
        graph = GraphWrapper(graph)

    # We only use successors, because gp_pred is optional, and it's wrapper
    # implementation is inefficient.
    pred_counts = dict.fromkeys(graph.vertices(), 0)
    vert_count = 0
    for vert in graph.vertices():
        vert_count += 1
        for succ_vert in graph.succ(vert):
            pred_counts[succ_vert] += 1

    # Necessary condition 1: All nodes have 1 predecessor execpt for the root,
    # which has no predecessors.
    root = None
    for node, count in pred_counts.items():
        if count == 0:
            root = node
            continue

        if count != 1:
            return None

    if root == None:
        return None

    # Necessary condition 2: All nodes are connected transitively from the
    # root.
    search = BreadthFirstSearch(graph, root)
    search.run()
    if len(search.visited) != vert_count:
        return None

    # BOTH necessary conditions being true is a sufficient condition that the
    # graph is a tree.
    return root

