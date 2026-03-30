from graphs import ADMG
from ci_tests import ci_test

def iterative_graph_expansion(x, y, gg=None, pocc=False, fast=False, verbose=False) -> set | None:
    """
    No-lookback version of confounder selection via iterative graph expansion of Guo & Zhao 2026.
    :param x: exposure node (must not be an outcome of y)
    :param y: outcome node (must not be a cause of x)
    :param gg: ground truth ADMG over the observable variables in the problem.
    :param pocc: if True, adding observed common causes is prioritized over adding mediators of unobserved causes in
    the get_primary_adjustment subroutine.
    :param fast: if pocc True and fast True, all observed common causes are added simultaneously in
    the get_primary_adjustment subroutine. Makes the algorithm faster for larger graphs.
    :param verbose: if True, the steps of the algorithm are printed while running.
    :return: a sufficient adjustment set for (x,y), or None if none exists.
    """
    
    def interactive_get_primary_adj(a, b, current_adjustment):
        primary_adjustment = set()
        while True:
            print(f"Is there a common cause of {a} and {b} whose effects are not fully mediated through "
                  f"{current_adjustment.union(primary_adjustment)}? (y/n)")
            response = input().lower()
            if response == 'y':
                print(f"Is this common cause observed? (y/n)")
                is_obs = input().lower()

                if is_obs == 'y':
                    print(f"What is the name of this common cause?")
                    cc_name = input()
                    primary_adjustment.add(cc_name)
                elif is_obs == 'n':
                    print(f"Is there a set of variables that either fully mediate the effects of this common cause on {a} "
                          f"or fully mediate the effects of this comon cause on {b}? (y/n)")
                    is_mediate = input().lower()
                    if is_mediate == 'y':
                        print(f"Please enter the set of these mediators separated by a comma (,)")
                        mediators = input().split(",")
                        primary_adjustment.update(set(mediators))
                    elif is_mediate == 'n':
                        print(f"Would you like to try with another common cause of {a} and {b}? (y/n)")
                        try_another = input().lower()
                        if try_another == 'y':
                            pass
                        elif try_another == 'n':
                            print(f"No primary adjustment set found for {a},{b}")
                            return None
                        else: # unaccepted input
                            raise ValueError("unacceptable input")
                    else:  # unaccepted input
                        raise ValueError("unacceptable input")
                else:  # unaccepted input
                    raise ValueError("unacceptable input")
            elif response == 'n':
                print(f"A primary adjustment set for {a} and {b} is {primary_adjustment}.")
                return primary_adjustment
            else:
                raise ValueError("unacceptable input")
    
    if gg is not None:
        if not isinstance(gg, ADMG):
            raise TypeError("The provided graph is not an ADMG.")
        # Graph provided. we will run an oracle version of get_primary_adjustment set
        g = gg.copy()
        for x_child in set(gg.node_children[x]):
            g.delete_directed_edge(x, x_child)
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
        if gg is not None:
            # oracle get_primary_adjustment using the provided graph:
            pas = g.get_primary_adjustment(edge[0], edge[1], current_adjustment=S_bar.difference({x, y}.union(edge)),
                                   prioritize_observed_common_causes=pocc, fast=fast, verbose=verbose)
        else:
            # elicit info interactively from the user:
            pas = interactive_get_primary_adj(edge[0], edge[1], S_bar.difference({x, y}.union(edge)))
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

def disjunctive_cause(x, y, g=None) -> set:
    """
    The disjunctive cause criterion for finding a sufficient adjustment set for x,y
    :param x: exposure node (must not be an outcome of y)
    :param y: outcome node (must not be a cause of x)
    :param g: ground truth ADMG over the observable variables in the problem.
    :return: a set of variables that are causes of either x or y. If there exists a sufficient adjustment set for (x,y),
    then the returned set is a sufficient adjustment set.
    """
    if g is not None:  # oracle access to the graph
        if not isinstance(g, ADMG):
            raise ValueError("The provided graph is not an ADMG.")
        x_anc = g.get_ancestors(x)
        y_anc = g.get_ancestors(y)
        disjunctive_causes = x_anc.union(y_anc)
    else:  # prompt the user for causes
        # ask the user to give the observed causes of x separated by a comma
        print(f"Please enter the observed causes of {x} separated by a comma (,). "
              f"If there are no observed causes, just press enter.")
        x_anc = input().split(",")
        print(f"Please enter the observed causes of {y} separated by a comma (,). "
              f"If there are no observed causes, just press enter.")
        y_anc = input().split(",")
        disjunctive_causes = set(x_anc).union(set(y_anc))
    return disjunctive_causes.difference({x, y})

def conjunctive_cause(x, y, g=None) -> set:
    """
    The conjunctive cause criterion for finding a sufficient adjustment set for x,y
    :param x: exposure node (must not be an outcome of y)
    :param y: outcome node (must not be a cause of x)
    :param g: ground truth ADMG over the observable variables in the problem.
    :return: a set of variables that are causes of both x and y.
    """
    if g is not None:
        if not isinstance(g, ADMG):
            raise ValueError("The provided graph is not an ADMG.")
        x_anc = g.get_ancestors(x)
        y_anc = g.get_ancestors(y)
        conjunctive_causes = x_anc.intersection(y_anc)
    else:  # prompt the user for common causes
        print(f"Please enter the observed common causes of {x} separated by a comma (,). "
              f"If there are no observed common causes, just press enter.")
        x_anc = input().split(",")
        print(f"Please enter the observed common causes of {y} separated by a comma (,). "
              f"If there are no observed common causes, just press enter.")
        y_anc = input().split(",")
        conjunctive_causes = set(x_anc).intersection(set(y_anc))
    return conjunctive_causes.difference({x, y})






