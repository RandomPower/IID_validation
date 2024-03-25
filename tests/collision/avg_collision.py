""" 5.1.7 Average Collision Test Statistic
average collision
"""

import numpy as np


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
