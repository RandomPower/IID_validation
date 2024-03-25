""" 5.1.9 Periodicity Test Statistics"""

import time

from utils.config import p
from utils.time_monitor_function import timed


# @timed
def periodicity(S, y):
    """Determines the number of periodic samples in the sequence

    Parameters
    ----------
    S : list of int
        sequence of sample values
    y : int
        lag parameter

    Returns
    -------
    int
        number of instances where an element in the sequence is equal to another element that is y positions ahead
    """
    T = 0
    for i in range(0, len(S) - y):
        if S[i] == S[i + y]:
            T += 1
    return T


def periodicity_test(S):
    T = []
    for k in p:
        t = 0
        for i in range(0, len(S) - k):
            if S[i] == S[i + k]:
                t += 1
        T.append(t)
    return T
