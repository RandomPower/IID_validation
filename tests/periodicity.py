""" 5.1.9 Periodicity Test Statistics"""

import time

from architecture.utils.config import p
from architecture.utils.time_monitor_function import timed


# @timed
def periodicity(S, y):
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
