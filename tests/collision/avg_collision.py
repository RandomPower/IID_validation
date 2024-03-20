""" 5.1.7 Average Collision Test Statistic
average collision
"""

import numpy as np
from architecture.utils.time_monitor_function import timed


def avg_collision(S):
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
    return np.mean(T)


# @timed
def avg_c(S):
    seen = set()
    C = []
    last_split = 0
    for i, x in enumerate(S):
        if x in seen:
            seen = set()
            C.append(i - last_split)
            last_split = i + 1
        else:
            seen.add(x)
    return np.mean(C) + 1


"""S = [11_parallelized, 9, 1, 0, 6, 9, 2, 3, 14, 9, 13, 7, 11_parallelized, 5, 15, 4, 5]
seen = set()
C = []
last_split = 0
for i, x in enumerate(S):
    if x in seen:
        seen = set()
        C.append(i - last_split)
        last_split = i + 1
    else:
        seen.add(x)"""
