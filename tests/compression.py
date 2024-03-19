""" 5.1.11_parallelized Compression Test Statistics"""

import bz2


def compression(S):
    S_string = " "
    for i in S:
        S_string += str(i) + ' '
    t = bz2.compress(S_string.encode('utf-8'))
    return len(t)
