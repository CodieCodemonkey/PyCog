Graph Protocols   {#graph-protocol}
===============

PyCog does not lock you into using any particular graph class.  Classes with graph-like behavior do not derive from a fixed type.  Instead you can use your preferred graph implementation by implementing this simple protocol.  If you'd rather, PyCog includes pycog.graph, which you can use as a mix-in to implement a graph.

Basic Graph Protocol
--------------------

For the purposes of this document, a class thats supports the basic graph protocol is called a _graph class_.  Instances of graph classes are called _graphs_.

From PyCog's point of view, all graphs are directed graphs.  An undirected graph is implemented by imposing the property that if `succ(a) == b`, then `succ(b) == a`.

#### Required Members

`vertices()` -- returns an iterator over the vertices of the graph.
`succ(v)` -- returns an iterator over the successors of vertex `v`.
`add_vertex(v)` -- adds vertex `v` to the graph.
`connect_vertices(v1, v2)` -- makes `v1` a successor of `v2`.

#### Optional Members

`pred(v)` -- returns an iterator over the predecessors of vertex `v`.  If this member is not available, PyCog class may need to build their own predecessor dictionary.
`num_vertices()` -- returns the number of vertices in the graph.  If this member is not implemented, PyCog will use the `vertices()` method to count them.
`vertex_type()` -- Returns the type of the vertices that may be used with this graph.  PyCog will extend this type to create vertices.  If this method is not present, PyCog will assume that it may use any object as a vertex.

#### Other Requirements

It must be possible for vertices to be members of multiple graphs simultaneously.  Two graphs that share vertices may have different edges connecting those vertices, so the connective information resides with the graph, not the vertex.  For this reason `succ()` and `pred()` are graph methods, not vertex methods.

Graph Algorithms
----------------

There are a number of common graph algorithms which PyCog may use.  Sometimes it may be more efficient to use equivalent algorithms provided by a third party.  PyCog will provide a mechanism to redirect such algorithms, although the specific method for doing that hasn't been defined yet.




