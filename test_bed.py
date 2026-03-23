from graphs import ADMG, DAG
from min_cut import min_vertex_cut

def test_min_cut():
    # Example usage for vertex cut
    dag = DAG()
    dag.add_directed_edge('A', 'B')
    dag.add_directed_edge('A', 'C')
    dag.add_directed_edge('B', 'E')
    dag.add_directed_edge('E', 'D')
    dag.add_directed_edge('C', 'D')
    print("Min vertex cut:", min_vertex_cut(dag, 'A', 'D'))

def test_primary_adj(verbose=False):
    g = ADMG()
    g.add_directed_edges([('X', 'Y'), ('M', 'X'), ('N', 'Y')])
    g.add_bidirected_edges([('X', 'M'), ('M', 'Y'), ('N', 'Y'), ('N', 'X')])

    pas = g.get_primary_adjustment('X', 'Y', prioritize_observed_common_causes=False, fast=False, verbose=verbose)
    if pas is None:
        print('No primary adjustment set found.')
    else:
        print(f'A minimal primary adjustment set for X and Y is {pas}.')

if __name__ == "__main__":
    verbose = True
    test_primary_adj(verbose)