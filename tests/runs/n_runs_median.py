""" 5.1.5 Number of Runs based on median"""

import utils.useful_functions


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
    S_prime = utils.useful_functions.s_prime_median(S)

    T = 1
    for i in range(1, len(S_prime)):
        if S_prime[i] != S_prime[i - 1]:
            T += 1
    return T
