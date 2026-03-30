"""
This module defines classes for representing different types of graphs,
including Acyclic Directed Mixed Graphs (ADMGs),
Directed Acyclic Graphs (DAGs), and undirected graphs.
"""
from collections import deque
from typing import Any
from utils import min_vertex_cut
from copy import deepcopy as copy


class ADMG:
    """
        A class representing an Acyclic Directed Mixed Graph (ADMG). It supports both directed and bidirected edges.
        The class provides methods to add nodes, directed edges, and bidirected edges,
        as well as a method to expand the ADMG into a DAG representation by introducing
        latent nodes for each bidirected edge.
    """
    def __init__(self) -> None:
        self.nodes = set()
        self.node_parents = {}  # parents of each node
        self.node_children = {}  # children of each node
        self.b_edges = {}  # bidirected edges
        self.dag = None  # cached DAG representation of the ADMG
        self.updated = False  # flag to track if the graph has been updated since the last DAG conversion

    def copy(self) -> 'ADMG':
        # return a copy of itself
        new_graph = ADMG()
        new_graph.nodes = copy(self.nodes)
        new_graph.node_parents = copy(self.node_parents)
        new_graph.node_children = copy(self.node_children)
        new_graph.b_edges = copy(self.b_edges)
        # new_graph.dag = None
        new_graph.updated = True
        return new_graph



    def add_node(self, node, bypass_name_restrictions=False) -> None:
        if not bypass_name_restrictions:
            # if the node name begins with "L", throw an error since we use "L" to denote latent nodes
            # in the DAG representation
            if isinstance(node, str) and node.startswith("L"):
                raise ValueError("Node names cannot start with "
                                 "'L' as they are reserved for latent nodes in the DAG representation.")
            # similarly, do not allow 'source' and 'sink' as node names since we use them for the min cut algorithm
            if isinstance(node, str) and node in {"source", "sink"}:
                raise ValueError("Node names cannot be 'source' or 'sink' as they are reserved for the min cut algorithm.")
        self.updated = True
        self.nodes.add(node)
        if node not in self.node_parents:
            self.node_parents[node] = set()
        if node not in self.node_children:
            self.node_children[node] = set()
        if node not in self.b_edges:
            self.b_edges[node] = set()

    def add_nodes(self, nodes, bypass_name_restrictions=False) -> None:
        for node in nodes:
            self.add_node(node, bypass_name_restrictions)

    def add_directed_edge(self, from_node, to_node) -> None:
        if from_node not in self.nodes:
            self.add_node(from_node)
        if to_node not in self.nodes:
            self.add_node(to_node)
        self.node_parents[to_node].add(from_node)
        self.node_children[from_node].add(to_node)

    def add_directed_edges(self, edge_list) -> None:
        for from_node, to_node in edge_list:
            self.add_directed_edge(from_node, to_node)

    def add_bidirected_edge(self, node1, node2) -> None:
        self.add_node(node1)
        self.add_node(node2)
        self.b_edges[node1].add(node2)
        self.b_edges[node2].add(node1)

    def add_bidirected_edges(self, edge_list) -> None:
        for node1, node2 in edge_list:
            self.add_bidirected_edge(node1, node2)

    def delete_bidirected_edge(self, node1, node2) -> None:
        if (node1 in self.nodes and node2 in self.nodes
                and node1 in self.b_edges[node2] and node2 in self.b_edges[node1]):
            self.b_edges[node1].remove(node2)
            self.b_edges[node2].remove(node1)
            return
        else:
            raise ValueError(f"Bidirectional edge between {node1} and {node2} not found.")

    def delete_directed_edge(self, node1, node2) -> None:
        if (node1 in self.nodes and node2 in self.nodes
                and node2 in self.node_children[node1] and node1 in self.node_parents[node2]):
            self.node_children[node1].remove(node2)
            self.node_parents[node2].remove(node1)
            return
        else:
            raise ValueError(f"Directed edge from {node1} to {node2} not found.")

    def is_bidirected_connected(self, node1, node2) -> bool:
        """Check if there is a bidirected path between node1 and node2."""
        visited = set()
        queue = deque([node1])
        visited.add(node1)

        while queue:
            current = queue.popleft()
            if current == node2:
                return True
            for neighbor in self.b_edges[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False


    def _get_dag(self) -> 'DAG':
        """
            Convert the ADMG to a DAG by introducing latent nodes for each bidirected edge.
        :return: A DAG representation of the ADMG.
        """
        dag = DAG()
        dag.add_nodes(self.nodes)
        dag.add_directed_edges([(u, v) for u in self.nodes for v in self.node_children[u]])

        latent_counter = 0
        for u in self.b_edges:
            for v in self.b_edges[u]:
                if u < v:  # to avoid double counting edges
                    latent_node = f"L{latent_counter}"
                    latent_counter += 1
                    dag.add_node(latent_node, bypass_name_restrictions=True)  # allow latent nodes to start with "L"
                    dag.add_directed_edge(latent_node, u)
                    dag.add_directed_edge(latent_node, v)

        return dag

    def _update_dag(self) -> None:
        if self.updated:
            self.dag = self._get_dag()
            self.updated = False

    def get_ancestors(self, node, not_through=None) -> set:
        """Get the ancestors of a node in the ADMG by traversing the directed edges.
        If not_through is provided, exclude ancestors that are connected through the specified nodes."""
        if not_through is None:
            not_through = set()
        ancestors = set()
        stack = [node]
        while stack:
            current = stack.pop()
            for parent in self.node_parents[current]:
                if parent not in ancestors and parent not in not_through:
                    ancestors.add(parent)
                    stack.append(parent)
        return ancestors

    def _get_dag_ancestors(self, node, not_through=None) -> set:
        """
            Get the ancestors of a node in the DAG representation of the ADMG.
            If not_through is provided, exclude ancestors that are connected through the specified nodes.
        """
        self._update_dag()
        return self.dag.get_ancestors(node, not_through)

    def get_subgraph(self, nodes, x=None, y=None) -> 'ADMG':
        """
            Get the subgraph of the ADMG induced by a set of nodes.
            if x and y are provided, the directed between x and y will be excluded from the subgraph.
        """
        subgraph = ADMG()
        subgraph.add_nodes(nodes, bypass_name_restrictions=True)  # allow nodes starting with "L" in the subgraph if
        # they already are included in the original graph.

        for node in nodes:
            for parent in self.node_parents[node]:
                if parent in nodes:
                    subgraph.add_directed_edge(parent, node)
            for child in self.node_children[node]:
                if child in nodes:
                    subgraph.add_directed_edge(node, child)
            for b_neighbor in self.b_edges[node]:
                if b_neighbor in nodes:
                    subgraph.add_bidirected_edge(node, b_neighbor)

        # Make sure there is no directed edge left between x and y if they are provided:
        if x is not None and y is not None:
            if x in subgraph.nodes and y in subgraph.nodes:
                subgraph.add_directed_edges({(y, x), (x, y)})
                subgraph.delete_directed_edge(x, y)
                subgraph.delete_directed_edge(y, x)

        return subgraph

    def _get_dag_ancestral_subgraph(self, nodes, not_through=None, x=None, y=None) -> tuple['DAG', set]:
        """
            Get the ancestral subgraph of a pair of nodes in the DAG representation of the ADMG.
            Also returns the set of common ancestors of the two nodes.
            If not_through is provided, exclude ancestors that are connected through the specified nodes.
            if x and y are provided, the directed edge from x to y will be excluded from the ancestral subgraph if it exists.
        """
        if len(nodes) != 2:
            raise ValueError("This method is designed for sets of size 2.")
        xx, yy = nodes
        self._update_dag()
        x_ancestors = self.dag.get_ancestors(xx, not_through.union({yy}))
        y_ancestors = self.dag.get_ancestors(yy, not_through.union({xx}))
        ancestral_nodes = x_ancestors.union(y_ancestors).union({xx, yy})
        ancestral_dag = self.dag.get_subgraph(ancestral_nodes, x=x, y=y)
        common_ancestors = x_ancestors.intersection(y_ancestors)
        return ancestral_dag, common_ancestors

    def get_primary_adjustment(self, x, y, current_adjustment=None,
                               prioritize_observed_common_causes=False, fast=False, verbose=False) -> set[Any] | None:
        """
            Get the primary adjustment set for a pair of nodes in the ADMG.
            This is a set of nodes that blocks all confounding arcs between x and y that are not already blocked
            by the current adjustment set.
            if prioritize_observed_common_causes is True, then we will prioritize adding observed common causes of
            x and y to the primary adjustment set over adding mediators of unobserved common causes.
            if prioritize_observed_common_causes and fast are both True, then we will add all non-latent common
            causes to the primary adjustment set. Otherwise, just pick one.
        """
        if verbose:
            print(f"getting primary adjustment set for {x} and {y} with current adjustment set {current_adjustment}...")
        def minimalize(adjustment_set):  # given an adjustment set, check if any nodes can be removed while still
            # blocking all confounding arcs between x and y.
            minimal_adjustment = set(adjustment_set)
            if verbose:
                print(f"minimalizing primary adjustment set: {adjustment_set}")
            for node in adjustment_set:
                test_adjustment = minimal_adjustment - {node}
                _, common_ancestors = self._get_dag_ancestral_subgraph({x, y}, not_through=current_adjustment.union(test_adjustment))
                if not common_ancestors:  # if there are no common ancestors left, then we can remove this node from the adjustment set
                    minimal_adjustment.remove(node)
                    if verbose:
                        print(f"removed {node} from primary adjustment set to minimize it")
            if verbose:
                print(f"---------------\n")
            return minimal_adjustment

        if current_adjustment is None:
            current_adjustment = set()
        ancestral_dag, common_ancestors = self._get_dag_ancestral_subgraph({x, y}, not_through=current_adjustment, x=x, y=y)
        # if common_ancestors is empty, then there are no confounding arcs between x and y that
        # are not already blocked by the current adjustment set, so we can return an empty set.
        if not common_ancestors:
            if verbose:
                print(f"---------------\n")
            return set()

        primary_adjustment = set()

        if prioritize_observed_common_causes:
            # get common ancestors that do not start with "L" (i.e. a non-latent common ancestor)
            non_latent_common_ancestors = [ancestor for ancestor in common_ancestors if not ancestor.startswith("L")]
            while non_latent_common_ancestors:
                if fast:
                    primary_adjustment.update(non_latent_common_ancestors)
                    if verbose:
                        print(f"added observed common causes to primary adjustment set: {non_latent_common_ancestors}")
                else:
                    primary_adjustment.add(non_latent_common_ancestors[0])
                    if verbose:
                        print(f"added observed common cause to primary adjustment set: {non_latent_common_ancestors[0]}")
                ancestral_dag, common_ancestors = self._get_dag_ancestral_subgraph(
                    {x, y}, not_through=current_adjustment.union(primary_adjustment), x=x, y=y)
                if not common_ancestors:
                    return minimalize(primary_adjustment)
                non_latent_common_ancestors = [ancestor for ancestor in common_ancestors if
                                               not ancestor.startswith("L")]

            # once out of the while loop, we know that all common ancestors are latent.
            # At this point, we need to add mediators that block the paths to one end point

            while common_ancestors:
                u = common_ancestors.pop()  # unobserved_common_cause
                if verbose:
                    print(f"unobserved common cause: {u}, confounding edge between {ancestral_dag.node_children[u]}")
                # solve two minimum vertex-cut problems: one for directed paths from u to x and one for
                # directed paths from u to y. add the smallest set to the primary adjustment set.
                # repeat until no common ancestors remain.
                min_cut_x, cut_cost_x = min_vertex_cut(ancestral_dag, u, x)
                min_cut_y, cut_cost_y = min_vertex_cut(ancestral_dag, u, y)
                if verbose:
                    if cut_cost_x == float('inf'):
                        print(f"no observed mediators from {u} to {x}")
                    else:
                        print(f"minimum mediator from {u} to {x}: {min_cut_x} with size {cut_cost_x}")
                    if cut_cost_y == float('inf'):
                        print(f"no observed mediators from {u} to {y}")
                    else:
                        print(f"minimum mediator from {u} to {y}: {min_cut_y} with size {cut_cost_y}")
                # choose the cut with the smaller cost and add it to the primary adjustment set if it is not infinity
                if cut_cost_x < cut_cost_y and cut_cost_x < float('inf'):
                    primary_adjustment.update(min_cut_x)
                    if verbose:
                        print(f"added {min_cut_x} to primary adjustment set to block paths from {u} to {x}")
                    ancestral_dag, common_ancestors = self._get_dag_ancestral_subgraph(
                        {x, y}, not_through=current_adjustment.union(primary_adjustment), x=x, y=y)
                elif cut_cost_y < float('inf'):
                    primary_adjustment.update(min_cut_y)
                    if verbose:
                        print(f"added {min_cut_y} to primary adjustment set to block paths from {u} to {y}")
                    ancestral_dag, common_ancestors = self._get_dag_ancestral_subgraph(
                        {x, y}, not_through=current_adjustment.union(primary_adjustment), x=x, y=y)
                else:
                    if verbose:
                        print(f"no observed mediators from {u} to either {x} or {y}. cannot block. skipping {u} for now.")
                    pass
        else:  # no prioritization, just iterate over common ancestors and add them to the primary adjustment set
            # if observed, add mediators if unobserved.
            while common_ancestors:
                ancestor = common_ancestors.pop()
                if verbose:
                    if ancestor.startswith("L"):
                        print(f"common cause: {ancestor} (unobserved), confounding edge between {ancestral_dag.node_children[ancestor]}")
                    else:
                        print(f"common cause: {ancestor}")
                if not ancestor.startswith("L"):  # if the common ancestor is observed, add it to the primary adjustment set
                    primary_adjustment.add(ancestor)
                    if verbose:
                        print(f"added {ancestor} to primary adjustment set")
                    ancestral_dag, common_ancestors = self._get_dag_ancestral_subgraph(
                        {x, y}, not_through=current_adjustment.union(primary_adjustment), x=x, y=y)
                else:  # if the common ancestor is latent, add mediators to the primary adjustment set
                    min_cut_x, cut_cost_x = min_vertex_cut(ancestral_dag, ancestor, x)
                    min_cut_y, cut_cost_y = min_vertex_cut(ancestral_dag, ancestor, y)
                    if verbose:
                        if cut_cost_x == float('inf'):
                            print(f"no observed mediators from {ancestor} to {x}")
                        else:
                            print(f"minimum mediator from {ancestor} to {x}: {min_cut_x} with size {cut_cost_x}")
                        if cut_cost_y == float('inf'):
                            print(f"no observed mediators from {ancestor} to {y}")
                        else:
                            print(f"minimum mediator from {ancestor} to {y}: {min_cut_y} with size {cut_cost_y}")
                    if cut_cost_x < cut_cost_y and cut_cost_x < float('inf'):
                        primary_adjustment.update(min_cut_x)
                        if verbose:
                            print(f"added {min_cut_x} to primary adjustment set to block paths from {ancestor} to {x}")
                        ancestral_dag, common_ancestors = self._get_dag_ancestral_subgraph(
                            {x, y}, not_through=current_adjustment.union(primary_adjustment), x=x, y=y)
                    elif cut_cost_y < float('inf'):
                        primary_adjustment.update(min_cut_y)
                        if verbose:
                            print(f"added {min_cut_y} to primary adjustment set to block paths from {ancestor} to {y}")
                        ancestral_dag, common_ancestors = self._get_dag_ancestral_subgraph(
                            {x, y}, not_through=current_adjustment.union(primary_adjustment), x=x, y=y)
                    else:
                        if verbose:
                            print(f"no observed mediators from {ancestor} to either {x} or {y}. cannot block. skipping {ancestor} for now.")
                        pass

        # if there are any common ancestors left, then they must be latent
        # and cannot be blocked by any adjustment set, so we can return None to indicate that no primary adjustment
        # set exists.
        _, common_ancestors = self._get_dag_ancestral_subgraph(
            {x, y}, not_through=current_adjustment.union(primary_adjustment))
        if common_ancestors:
            if verbose:
                print(f"remaining common causes that cannot be blocked by any adjustment set: {common_ancestors}")
                print(f"no primary adjustment set exists.")
                print(f"---------------\n")
            return None
        else:
            return minimalize(primary_adjustment)




class DAG(ADMG):
    """
        A class representing a Directed Acyclic Graph (DAG).
        It inherits from the ADMG class but does not support bidirected edges.
    """
    def __init__(self) -> None:
        super().__init__()

    # add_directed_edge is inherited from Graph. add_edge does the same thing as
    # add_directed_edge:
    def add_edge(self, from_node, to_node) -> None:
        self.add_directed_edge(from_node, to_node)

    def add_edges(self, edge_list) -> None:
        self.add_directed_edges(edge_list)

    # no bidirected edges in DAG
    def add_bidirected_edge(self, node1, node2) -> None:
        raise NotImplementedError("DAGs do not support bidirected edges.")

    def add_bidirected_edges(self, edge_list) -> None:
        raise NotImplementedError("DAGs do not support bidirected edges.")



class WeightedDAG(DAG):
    """
        A class representing a Weighted Directed Acyclic Graph (Weighted DAG).
        It inherits from the DAG class and adds support for edge weights.
        This class supports a minimum cut algorithm.
    """
    def __init__(self) -> None:
        super().__init__()
        self.edge_weights = {}  # dictionary to store edge weights, keys are (from_node, to_node) tuples

    def add_directed_edge(self, from_node, to_node, weight=1.0) -> None:
        super().add_directed_edge(from_node, to_node)
        self.edge_weights[(from_node, to_node)] = weight

    def add_directed_edges(self, edge_list) -> None:
        for from_node, to_node, weight in edge_list:
            self.add_directed_edge(from_node, to_node, weight)

    def _bfs(self, flow_graph, source, sink, parent) -> bool:
        visited = set()
        queue = deque([source])
        visited.add(source)

        while queue:
            u = queue.popleft()
            for v in flow_graph[u]:
                if v not in visited and flow_graph[u][v] > 0:  # check for positive residual capacity
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)
                    if v == sink:
                        return True
        return False

    def _edmond_karps(self, flow_graph, source, sink) -> tuple[dict, float]:
        parent = {}
        max_flow = 0

        while self._bfs(flow_graph, source, sink, parent):
            path_flow = float('inf')
            s = sink

            while s != source:
                path_flow = min(path_flow, flow_graph[parent[s]][s])
                s = parent[s]

            max_flow += path_flow

            v = sink
            while v != source:
                u = parent[v]
                flow_graph[u][v] -= path_flow
                if v not in flow_graph:
                    flow_graph[v] = {}
                if u not in flow_graph[v]:
                    flow_graph[v][u] = 0
                flow_graph[v][u] += path_flow
                v = parent[v]

        return flow_graph, max_flow

    def min_cut(self, source, sink) -> tuple[set, float]:
        """
            Compute the minimum cut between source and sink in the DAG using the Edmonds-Karp algorithm.
        """
        # Create a residual graph
        residual_graph = {u: {v: self.edge_weights.get((u, v), 0) for v in self.node_children[u]} for u in self.nodes}
        print(f"Residual graph before max flow: {residual_graph}")
        # Calculate max flow using Edmonds-Karp algorithm
        residual_graph, _ = self._edmond_karps(residual_graph, source, sink)

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
        cut_edges = set()
        for u in visited:
            for v in self.node_children[u]:
                if v not in visited and self.edge_weights.get((u, v), 0) > 0:
                    cut_edges.add((u, v))
        print(f"Cut edges: {cut_edges}")
        print(f"Cut value: {sum(self.edge_weights.get(edge, 0) for edge in cut_edges)}")
        return cut_edges, sum(self.edge_weights.get(edge, 0) for edge in cut_edges)