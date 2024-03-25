""" 5.1.2 Number of Directional Runs"""


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
    S_prime = []
    for i in range(len(S) - 1):
        if S[i] > S[i + 1]:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0
    # S_prime should be len(S) - 1

    T = 1
    for k in range(1, len(S_prime)):
        if S_prime[k] != S_prime[k - 1]:
            T += 1
    return T


"""S = [2, 2, 2, 5, 7, 7, 9, 3, 1, 4, 4]
T = n_directional_runs(S)
print(T)"""
