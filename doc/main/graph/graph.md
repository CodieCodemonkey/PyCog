Graph Protocol   {#graph-protocol}
==============

PyCog does not lock you into using any particular graph class.  Classes with graph-like behavior do not derive from a fixed type.  Instead you can use your preferred graph implementation by implementing this simple protocol.  If you'd rather, PyCog includes pycog.graph.Graph, which you can use as a mix-in to implement a graph.

For the purposes of this document, a class thats supports the graph protocol is called a _graph class_.  Instances of graph classes are called _graphs_.

Graph protocol methods are prefixed with 'gp_' to reduce the risk of a name collision.  This is similar to Python's use of `__..__` to identify protocol members such as `__iter__`.

From PyCog's point of view, a graph is a collection of vertices, with the additional notion that one element (called a "vertex" or "node" by convention) may be a successor of another element.  Everything one might want to know about a graph and the connectivity of its vertices may be derived from this simple definition.  Therefore the required methods of the graph protocol only require support for this definition.  The recommended and optional methods should be implemented when efficiency gains can be made.

All PyCog graphs are directed graphs.  An undirected graph is implemented by imposing the property that adjacent vertices are successors of each other.

#### Required Members

<dl>
  <dt>`graph.gp_vertices()`</dt><dd>Returns an iterator over the vertices of the graph.</dd>
  <dt>`graph.gp_succ(v)`</dt><dd>Returns an iterator over the successors of vertex `v`.  `KeyError` should be raised if the vertex is not in the graph.</dd>
  <dt>`graph.gp_add(v)`</dt><dd>Adds vertex `v` to the graph.</dd>
  <dt>`graph.gp_remove(v)`</dt><dd>Removes vertex `v` from the graph.</dd>
  <dt>`graph.gp_connect(v1, v2)`</dt><dd>Makes `v1` a successor of `v2`.</dd>
  <dt>`graph.gp_disconnect(v1, v2)`</dt><dd>Removes edge `v1`, `v2`.</dd>
</dl>

#### Recommended Members

These methods are not required since some graph implementations may not support them, but they are recommended for performance reasons.

<dl>
  <dt>`gp_pred(v)`</dt><dd>Returns an iterator over the predecessors of vertex `v`.  If this member is not available, PyCog class may need to build their own predecessor dictionary.  `gp_pred` must satisfy the relation **b in graph.gp_pred(a) if and only if a in graph.gp_succ(b)**.  In plain language, a vertex must be a successor of all its predecessors, and it must be a predecessor of all its successors.  `KeyError` should be raised if the vertex is not in the graph.</dd>
</dl>

#### Optional Members

<dl>
  <dt>`gp_clear()`</dt><dd>Remove all vertices from the graph.</dd>
  <dt>`gp_num_vertices()`</dt><dd>Returns the number of vertices in the graph.  If this member is not implemented, PyCog will use the `gp_vertices()` method to count them when needed.</dd>
  <dt>`in_degree(v)`</dt><dd>Returns the number of predecessor of `v`.`KeyError should be raised if `v` is not in the graph.</dd>
  <dt>`out_degree(v)`</dt><dd>Returns the number of successors of `v`.`KeyError should be raised if `v` is not in the graph.</dd>
  <dt>`gp_vertex_type()`</dt><dd>Returns the type of the vertices that may be used with this graph.  PyCog will extend this type to create vertices.  If this method is not present, PyCog will assume that it may use any object as a vertex.</dd>
</dl>

You can see what PyCog does in the absence of optional members by looking at graph_wrapper source.  graph_wrapper is PyCog's wrapper for graph classes.

#### Other Requirements

It must be possible for vertices to be members of multiple graphs simultaneously.  Two graphs that share vertices may have different edges connecting those vertices, so the connective information resides with the graph, not the vertex.  For this reason `gp_succ()` and `gp_pred()` are graph methods, not vertex methods.

Graph Algorithms
----------------

There are a number of common graph algorithms which PyCog may use.  Sometimes it may be more efficient to use equivalent algorithms provided by a third party.  PyCog will provide a mechanism to redirect such algorithms, although the specific method for doing that hasn't been defined yet.

