# Confounder-Selection

This repository contains code for several approaches to confounder selection, including:
- The conjunctive cause criterion (CCC)
- The disjunctive cause criterion (DCC)
- The minimal disjunctive cause criterion: apply DCC, and then remove any variable that is not a confounder given the others.
- The iterative graph expansion algorithm
- The treatment Markov boundary criterion
- The outcome Markov boundary criterion
- The iterative Markov boundary criterion: apply the treatment and outcome Markov boundary criteria alternately until convergence.
- More approaches to be added soon!

To install the dependencies in `requirements.txt` to run the code:
```bash
pip install -r requirements.txt
```
Note that if you do not want to run the conditional-independence-based algorithms, you can skip installing the `causal-learn` package, which is only used for performing conditional independence tests.
In that case, run 
```bash
pip install -r requirements_no_causal_learn.txt
```
instead.

The code is organized into the following files:
- test_bed.py: Contains example code to generate ADMGs, and to test the confounder selection algorithms on them.
- algorithms.py: Contains the implementation of the confounder selection algorithms.
- graphs.py: Contains the ADMG and DAG classes, with built-in functions for d-separation and m-separation, ancestors, etc.
- ci_tests.py: Contains code to perform conditional independence tests using the causal-learn package.
- utils.py: Contains utility functions for the algorithms and testing.