""" 5.1.4 Number of Increases and Decreases"""

import utils.useful_functions


def n_increases_decreases(S):
    """Measures the maximum number of increases or decreases between consecutive sample values

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        greater number between the total counts of increases and decreases among consecutive sample values
    """
    S_prime = utils.useful_functions.s_prime(S)

    count_plus = 0
    count_minus = 0

    for k in range(len(S_prime)):
        if S_prime[k] == -1:
            count_minus += 1
        else:
            count_plus += 1
    return max(count_minus, count_plus)
