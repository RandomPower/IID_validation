""" 5.1.6 Length of Runs based on median"""

import numpy as np


def l_median_runs(S):
    X = np.median(S)
    S_prime = []
    for i in range(len(S)):
        if S[i] < X:  # PROBLEM: 7 = 7.0 GIVES +1
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0
    # print(S_prime)

    T = 0
    current_count = 1  # Initialize with 1 for the first item

    for k in range(0, len(S_prime) - 1):
        if S_prime[k] == S_prime[k + 1]:
            current_count += 1
        else:
            if current_count > T:
                T = current_count
                current_count = 1

    # Check one more time after the loop for the last sequence
    if current_count > T:
        T = current_count

    return T


"""S = (5, 15, 12_normal, 1, 13, 9, 4)
print(l_median_runs(S))"""
