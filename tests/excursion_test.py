""" 5.1.1 Excursion Test Statistics"""

import numpy as np


def excursion_test(S):
    X = np.mean(S)
    D = [None] * len(S)
    somma = 0
    for i in range(1, len(S) + 1):
        somma += S[i - 1]
        D[i - 1] = np.abs(somma - (i * X))
    return max(D)
