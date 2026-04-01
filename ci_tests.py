"""
    A variety of tests can be implemented depending on the nature of the data,
    the size of the sample, and what is known about the data generating mechanism.
    For now, the code is based on the causal-learn package: https://causal-learn.readthedocs.io/en/latest/index.html
    This toolbox may be expanded in the future.
    Other conditional independence tests may also be provided by the user.
    A potentially useful package: https://github.com/shimenghuang/pycomets
"""

import numpy as np
import pandas as pd
from causallearn.utils.cit import CIT

def ci_test_df(df, x_col, y_col, z_cols=None, method="fisherz"):
    """
        df: dataset, pandas DataFrame
        x_col, y_col: column names (strings)
        z_cols: list of column names (conditioning set), one column name (string), or None
        method: "fisherz", "kci", "chisq", "gsq"
    """
    if z_cols is None:
        z_cols = []
    if isinstance(z_cols, str):
        z_cols = [z_cols]

    # Extract data
    x = df[[x_col]].to_numpy()
    y = df[[y_col]].to_numpy()

    if len(z_cols) > 0:
        z = df[z_cols].to_numpy()
    else:
        z = np.empty((len(df), 0))  # no conditioning variables

    # Combine into single dataset
    data = np.hstack([x, y, z])
    cit = CIT(data, method)

    z_inds = list(range(2, 2 + z.shape[1]))
    pval = cit(0, 1, z_inds)

    return pval

if __name__ == "__main__":
    import pandas as pd
    import numpy as np

    rng = np.random.default_rng(42)
    n = 400

    df = pd.DataFrame({
        "Z1": rng.normal(size=n),
        "Z2": rng.normal(size=n),
        "Z3": rng.normal(size=n),
        "Z4": rng.normal(size=n),
    })

    df["X"] = df["Z1"] + rng.normal(size=n)
    df["Y"] = df["Z1"] - df["Z3"] + rng.normal(size=n)

    # Run CI test
    pval = ci_test_df(df, "X", "Y", ["Z1", "Z2", "Z3", "Z4"], method="kci")

    print("p-value:", pval)