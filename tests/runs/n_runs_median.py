""" 5.1.5 Number of Runs based on median"""

import numpy as np


def n_median_runs(S):
    """Measures the number of runs that are constructed with respect to the median of the sequence

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        number of runs
    """
    X = np.median(S)
    S_prime = []
    for i in range(len(S)):
        if S[i] < X:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0

    T = 1
    for i in range(1, len(S_prime)):
        if S_prime[i] != S_prime[i - 1]:
            T += 1
    return T
