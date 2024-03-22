""" 5.1.8 Maximum Collision Test Statistic"""

import numpy as np
from utils.time_monitor_function import timed


def max_collision(S):
    i = 0
    seen_numbers = []
    T = []
    while i < len(S) - 1:
        for j in range(i, len(S)):
            if S[j] in seen_numbers:
                T.append(j + 1 - i)
                seen_numbers.clear()
                i = j + 1
            else:
                seen_numbers.append(S[j])
    return np.max(T)


# @timed
def max_c(S):
    seen = set()
    C = []
    last_split = 0
    for i, x in enumerate(S):
        if x in seen:
            seen = set()
            C.append(i + 1 - last_split)
            last_split = i + 1
        else:
            seen.add(x)
    return np.max(C) + 1
