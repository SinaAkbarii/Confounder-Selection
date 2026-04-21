from graphs import ADMG, DAG
from utils import min_vertex_cut
from algorithms import (iterative_graph_expansion, disjunctive_cause, conjunctive_cause, treatment_outcome_mb,
                        minimal_disjunctive_cause)


def gen_graph() -> ADMG:
    g = ADMG()
    g.add_directed_edges([('X', 'Y'), ('M', 'X'), ('N', 'Y')])
    g.add_bidirected_edges([('M', 'Y'), ('N', 'X')])
    return g


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
    g = gen_graph()
    pas = g.get_primary_adjustment('X', 'Y', prioritize_observed_common_causes=pocc, fast=fast, verbose=verbose)
    if pas is None:
        print('No primary adjustment set found.')
    else:
        print(f'A minimal primary adjustment set for X and Y is {pas}.')

def test_iterative_graph_expansion(g=None, pocc=False, fast=False, verbose=False):
    C = iterative_graph_expansion('X', 'Y', g, pocc=pocc, fast=fast, verbose=verbose)
    if C is None:
        print('Iterative graph expansion: No sufficient adjustment set found.')
    else:
        print(f'Iterative graph expansion: {C}.')

def test_conjunctive_disjunctive(g=None) -> None:
    print(f"Conjunctive Cause Criterion:{conjunctive_cause('X', 'Y', g)}")
    print(f"Disjunctive Cause Criterion:{disjunctive_cause('X', 'Y', g)}")
    print(f"Minimalized Disjunctive Cause Criterion: {minimal_disjunctive_cause('X', 'Y', g)}")

def test_markov_boundary(g=None, data=None, ci_method="fisherz", pval_th=0.05):
    tmb = treatment_outcome_mb('X', None, g, data, ci_method=ci_method, pval_th=pval_th)
    omb = treatment_outcome_mb('X', 'Y', g, data, ci_method=ci_method, pval_th=pval_th)
    print(f"Treatment Markov Boundary: {tmb}")
    print(f"Treatment Markov Boundary: {omb}")

def oracle_test(pocc=False, fast=False, verbose=True):
    g = gen_graph()
    test_iterative_graph_expansion(g, pocc=pocc, fast=fast, verbose=verbose)
    test_conjunctive_disjunctive(g)
    test_markov_boundary(g)





if __name__ == "__main__":
    oracle = True # if True, the true ADMG is provided and the algorithms works based on that.
    # otherwise they interact with the user to elicit information.
    verbose = True  # if True, the steps of the algorithms are printed throughout.
    pocc = False  # a parameter of the iterative graph expansion algorithm only.
    # it determines whether (True) or not (False) the algorithm prioritizes adding the observed common causes to
    # the current adjustment set over adding mediators of unobserved common causes.
    fast = False  # a parameter of the iterative graph expansion algorithm only.
    # the faster version of the algorithm adds every observed comon cause to the primary adjustment set at the
    # same time rather than adding them one by one. It might be worthwhile for large graphs.


    oracle_test(pocc=pocc, fast=fast, verbose=verbose)