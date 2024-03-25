""" 5.1.6 Length of Runs based on median"""

import numpy as np


def l_median_runs(S):
    X = np.median(S)
    S_prime = []
    for i in range(len(S)):
        if S[i] < X:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0

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
