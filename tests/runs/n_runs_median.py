""" 5.1.5 Number of Runs based on median"""

import numpy as np


def n_median_runs(S):
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
