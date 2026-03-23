from graphs import ADMG, DAG
from min_cut import min_vertex_cut
from algorithms import confounder_select_knowngraph

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

def test_confounder_select(pocc=False, fast=False, verbose=False):
    g = ADMG()
    g.add_directed_edges([('X', 'Y'), ('M', 'X'), ('N', 'Y')])
    g.add_bidirected_edges([('M', 'Y'), ('N', 'X')]) # ('X', 'M'), ('N', 'Y'),

    C = confounder_select_knowngraph('X', 'Y', g, pocc=pocc, fast=fast, verbose=verbose)
    if C is None:
        print('No sufficient adjustment set found.')
    else:
        print(f'A sufficient adjustment set for X and Y is {C}.')

if __name__ == "__main__":
    verbose = True
    pocc = True  # whether the algorithm prioritizes adding the observed common causes to the set over
    # adding mediators of unobserved common causes
    fast = False # the faster version of the algorithm adds every observed comon cause to the primary set at the
    # same time rather than adding them one by one. It might be worthwhile for large graphs.
    test_confounder_select(pocc, fast, verbose)