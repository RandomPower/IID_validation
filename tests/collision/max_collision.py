""" 5.1.8 Maximum Collision Test Statistic"""

import numpy as np


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
