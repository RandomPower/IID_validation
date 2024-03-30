""" 5.1.2 Number of Directional Runs"""

import utils.useful_functions


def n_directional_runs(S):
    """Measures the number of runs constructed using the relations between consecutive samples

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        number of runs
    """
    S_prime = utils.useful_functions.s_prime(S)

    T = 1
    for k in range(1, len(S_prime)):
        if S_prime[k] != S_prime[k - 1]:
            T += 1
    return T
