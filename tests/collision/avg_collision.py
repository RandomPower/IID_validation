""" 5.1.7 Average Collision Test Statistic
average collision
"""

import numpy as np


def avg_c(S):
    """Counts the number of successive sample values until a duplicate is found

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
       average length of subsequences with unique sample values before encountering a duplicate
    """
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
