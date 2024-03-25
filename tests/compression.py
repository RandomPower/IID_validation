""" 5.1.11_parallelized Compression Test Statistics"""

import bz2


def compression(S):
    """Removes redundancy in the sequnce, involving commonly recurring subsequences of characters.
    Encodes input data as a character string containing a list of values separated by a single
    space. Compresses the character string with the bzip2 compression algorithm

    Parameters
    ----------
    S : list of int
        sequence of sample values

    Returns
    -------
    int
        length of the compressed string
    """
    S_string = " "
    for i in S:
        S_string += str(i) + " "
    t = bz2.compress(S_string.encode("utf-8"))
    return len(t)
