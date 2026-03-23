from graphs import ADMG

def confounder_select_knowngraph(x, y, G:'ADMG', pocc=False, fast=False, verbose=False) -> set | None:
    """
    Confounder selection via iterative graph expansion of Guo & Zhao 2026.
    :param x: exposure node (must not be an outcome of y)
    :param y: outcome node (must not be a cause of x)
    :param G: ground truth ADMG over the observable variables in the problem.
    :param pocc: if True, adding observed common causes is prioritized over adding mediators of unobserved causes in
    the get_primary_adjustment subroutine.
    :param fast: if pocc True and fast True, all observed common causes are added simultaneously in
    the get_primary_adjustment subroutine. Makes the algorithm faster for larger graphs.
    :param verbose: if True, the steps of the algorithm are printed while running.
    :return: a sufficient adjustment set for (x,y), or None if none exists.
    """
    g = G.copy()
    for x_child in set(G.node_children[x]):
        g.delete_directed_edge(x, x_child)
    print(f'children of {x} in the original graph: {G.node_children[x]}')
    if x not in g.nodes or y not in g.nodes:
        raise ValueError(f"Both {x} and {y} must be in the graph.")

    # initiate the expanded graph:
    expanded_graph = ADMG()
    expanded_graph.add_bidirected_edge(x, y)

    # initiate the certainly confounded graph: an edge exists between a and be if there is no primary adjustment set
    # between a and be
    confounded_graph = ADMG() # represents the edges in B_y in the paper
    confounded_graph.add_nodes([x,y])

    def select_edge() -> tuple[str, str] | None:
        # select a bidirected edge from the expanded_graph that does not appear in the confounded_graph:
        for a in expanded_graph.nodes:
            for b in expanded_graph.b_edges[a]:
                if not b in confounded_graph.b_edges[a]:
                    return a, b
        return None

    def graph_expand():
        # if x and y are connected through B_y (the edges we are sure exist in the expanded graph,
        # then there is no sufficient adjustment set for x and y:
        if confounded_graph.is_bidirected_connected(x, y):
            if verbose:
                print(f"{x} and {y} are connected in the confounded graph. No sufficient adjustment set exists.\n---------------\n")
            return None
        # if x and y are disconnected, then S is a sufficient adjustment set:
        elif not expanded_graph.is_bidirected_connected(x, y):
            if verbose:
                print(f"{x} and {y} are disconnected in the expanded graph. A sufficient adjustment set found.\n---------------\n")
            return expanded_graph.nodes.difference({x, y})

        # otherwise, expand the graph:
        edge = select_edge()
        if verbose:
            print("Selected edge to expand: ", edge)
        if edge is None:
            # raise an exception because this can only happen do to a bug:
            raise Exception("No edge to select. This can only be due to a bug in the code.")
        # find a primary adjustment set for edge:
        S_bar = set(expanded_graph.nodes)
        pas = g.get_primary_adjustment(edge[0], edge[1], current_adjustment=S_bar.difference({x, y}.union(edge)),
                               prioritize_observed_common_causes=pocc, fast=fast, verbose=verbose)

        if pas is None:  # if no primary adjustment set, add edge to the confounded graph
            if verbose:
                print(f"No primary adjustment set found for edge {edge}. Adding it to the confounded graph.\n---------------\n")
            confounded_graph.add_bidirected_edge(edge[0], edge[1])
        else:  # if there is a primary adjustment set, expand the graph and delete edge:
            if verbose:
                print(f"Primary adjustment set found for edge {edge}: {pas}. Expanding...")
            expanded_graph.delete_bidirected_edge(edge[0], edge[1])
            for v in pas.difference(S_bar):
                for s in S_bar:
                    expanded_graph.add_bidirected_edge(v, s)
                confounded_graph.add_node(v)
                # add edges between every pair of nodes in pas:
                for v2 in pas.difference(S_bar):
                    if v != v2:
                        expanded_graph.add_bidirected_edge(v, v2)

        # iterate recursively
        return graph_expand()

    return graph_expand()


