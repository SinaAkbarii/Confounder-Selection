from graphs import ADMG, DAG
from min_cut import min_vertex_cut
from algorithms import iterative_graph_expansion, disjunctive_cause, conjunctive_cause

def test_min_cut():
    # Example usage for vertex cut
    dag = DAG()
    dag.add_directed_edge('A', 'B')
    dag.add_directed_edge('A', 'C')
    dag.add_directed_edge('B', 'E')
    dag.add_directed_edge('E', 'D')
    dag.add_directed_edge('C', 'D')
    print("Min vertex cut:", min_vertex_cut(dag, 'A', 'D'))

def test_primary_adj(pocc=False, fast=False, verbose=False):
    g = ADMG()
    g.add_directed_edges([('X', 'Y'), ('M', 'X'), ('N', 'Y')])
    g.add_bidirected_edges([('X', 'M'), ('M', 'Y'), ('N', 'Y'), ('N', 'X')])

    pas = g.get_primary_adjustment('X', 'Y', prioritize_observed_common_causes=pocc, fast=fast, verbose=verbose)
    if pas is None:
        print('No primary adjustment set found.')
    else:
        print(f'A minimal primary adjustment set for X and Y is {pas}.')

def test_iterative_graph_expansion(oracle=True, pocc=False, fast=False, verbose=False):
    g = ADMG()
    g.add_directed_edges([('X', 'Y'), ('M', 'X'), ('N', 'Y')])
    g.add_bidirected_edges([('M', 'Y'), ('N', 'X')]) # ('X', 'M'), ('N', 'Y'),

    if oracle:
        C = iterative_graph_expansion('X', 'Y', g, pocc=pocc, fast=fast, verbose=verbose)
    else:
        C = iterative_graph_expansion('X', 'Y')
    if C is None:
        print('Iterative graph expansion: No sufficient adjustment set found.')
    else:
        print(f'Iterative graph expansion: {C}.')

def test_conjunctive_disjunctive(oracle=True) -> None:
    if oracle:
        g = ADMG()
        g.add_directed_edges([('X', 'Y'), ('M', 'X'), ('N', 'Y')])
        g.add_bidirected_edges([('M', 'Y'), ('N', 'X')])  # ('X', 'M'), ('N', 'Y'),
    else:
        g = None

    print(f"Conjunctive Cause Criterion:{conjunctive_cause('X', 'Y', g)}")
    print(f"Disjunctive Cause Criterion:{disjunctive_cause('X', 'Y', g)}")




if __name__ == "__main__":
    oracle = True # if True, the true ADMG is provided and the algorithm works based on that.
    # otherwise it interacts with the user to elicit information.
    verbose = True  # if True, the steps of the algorithm are printed throughout.
    pocc = False  # whether the algorithm prioritizes adding the observed common causes to the set over
    # adding mediators of unobserved common causes
    fast = False # the faster version of the algorithm adds every observed comon cause to the primary set at the
    # same time rather than adding them one by one. It might be worthwhile for large graphs.
    test_iterative_graph_expansion(oracle, pocc, fast, verbose)

    test_conjunctive_disjunctive(oracle)