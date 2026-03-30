"""
    A variety of tests can be implemented depending on the nature of the data,
    the size of the sample, and what is known about the data generating mechanism.
    For now, the code is based on the causal-learn package: https://causal-learn.readthedocs.io/en/latest/index.html
    This toolbox may be expanded in the future.
    Other conditional independence tests may also be provided by the user.
    A potentially useful package: https://github.com/shimenghuang/pycomets
"""

import numpy as np
from causallearn.utils.cit import CIT

def ci_test(X, Y, Z, method="fisherz"):
    """
    X: shape (n,) or (n,1)
    Y: shape (n,) or (n,1)
    Z: shape (n,k)   multidimensional conditioning set
    method: "fisherz" and "kci" for continuous data,
    or "chisq" and "gsq" for discrete data
    """
    X = np.asarray(X).reshape(-1, 1)
    Y = np.asarray(Y).reshape(-1, 1)
    Z = np.asarray(Z)

    if Z.ndim == 1:
        Z = Z.reshape(-1, 1)

    data = np.hstack([X, Y, Z])
    cit = CIT(data, method)

    z_inds = list(range(2, 2 + Z.shape[1]))
    pval = cit(0, 1, z_inds)
    return pval

# Example use:
rng = np.random.default_rng(42)
n = 400
Z = rng.normal(size=(n, 4))
X = Z[:, 0] + rng.normal(size=n)
Y = Z[:, 0] - Z[:, 2] + rng.normal(size=n)

pval = ci_test(X, Y, Z, method="kci")
print("p-value:", pval)