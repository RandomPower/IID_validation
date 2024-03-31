""" 5.1.6 Length of Runs based on median"""

import utils.useful_functions


def l_median_runs(S):
    """Measures the length of the longest run constructed with respect to the median of the sequence

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        length of the longest run
    """
    S_prime = utils.useful_functions.s_prime_median(S)

    T = 0
    current_count = 1

    for k in range(0, len(S_prime) - 1):
        if S_prime[k] == S_prime[k + 1]:
            current_count += 1
        else:
            if current_count > T:
                T = current_count
                current_count = 1

    if current_count > T:
        T = current_count

    return T
