"""
    an implementation of the min cut algorithm using the Edmonds-Karp method for finding the maximum flow in a
    flow network.
"""

from collections import deque

def bfs(graph, source, sink, parent) -> bool:
    visited = set()
    queue = deque([source])
    visited.add(source)

    while queue:
        u = queue.popleft()

        for v in graph[u]:
            if v not in visited and graph[u][v] > 0:  # Check for positive capacity
                visited.add(v)
                parent[v] = u
                queue.append(v)

                if v == sink:
                    return True

    return False

def edmonds_karp(graph, source, sink) -> float:
    parent = {}
    max_flow = 0.0

    while bfs(graph, source, sink, parent):
        path_flow = float('inf')
        s = sink

        while s != source:
            # print("parent:", parent)
            path_flow = min(path_flow, graph[parent[s]][s])
            s = parent[s]

        max_flow += path_flow

        v = sink
        while v != source:
            u = parent[v]
            graph[u][v] -= path_flow
            graph[v][u] += path_flow
            v = parent[v]

    return max_flow

def min_cut(graph, source, sink) -> tuple[list[tuple[str, str]], float]:
    # Create a residual graph
    residual_graph = {u: {v: graph[u][v] for v in graph[u]} for u in graph}
    # print("Residual graph:", residual_graph)

    # Calculate max flow using Edmonds-Karp algorithm
    edmonds_karp(residual_graph, source, sink)
    # print("Residual graph after max flow:", residual_graph)

    # Find reachable vertices from the source in the residual graph
    visited = set()
    queue = deque([source])
    visited.add(source)

    while queue:
        u = queue.popleft()

        for v in residual_graph[u]:
            if v not in visited and residual_graph[u][v] > 0:
                visited.add(v)
                queue.append(v)

    # The edges that are from a reachable vertex to a non-reachable vertex are part of the min cut
    cut_edges = []
    for u in visited:
        for v in graph[u]:
            if v not in visited and graph[u][v] > 0:
                cut_edges.append((u, v))
    # return the cut edges and the total capacity of the cut (which is equal to the max flow)
    return cut_edges, sum(graph[u][v] for u, v in cut_edges)

def min_vertex_cut(graph, source, sink) -> tuple[set, float]:
    # reduce vertex cut to edge cut by splitting each vertex into two and connecting them with an edge of capacity equal
    # to 1 if the vertex is observd, and infinity if the vertex is latent.
    vertex_graph = {}
    for u in graph.nodes:
        vertex_graph[u + "_in"] = {}
        vertex_graph[u + "_out"] = {}
        if u == source or u == sink or u.startswith("L"):  # source, sink, or latent vertex
            vertex_graph[u + "_in"][u + "_out"] = float('inf')  # capacity of the vertex
        else:  # observed vertex
            vertex_graph[u + "_in"][u + "_out"] = 1  # capacity of the vertex
        vertex_graph[u + "_out"][u + "_in"] = 0
    for u in graph.nodes:
        for v in graph.node_children[u]:
            vertex_graph[u + "_out"][v + "_in"] = float('inf')  # capacity of the edge
            vertex_graph[v + "_in"][u + "_out"] = 0

    # Now we can find the min cut in the vertex graph
    edge_cut, cut_capacity = min_cut(vertex_graph, source + "_in", sink + "_out")
    # Convert edge cut back to vertex cut
    vertex_cut = set()
    for u, v in edge_cut:
        if u.endswith("_in") and v.endswith("_out"):
            vertex_cut.add(u[:-3])  # add the original vertex name
    return vertex_cut, cut_capacity


