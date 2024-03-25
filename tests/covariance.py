""" 5.1.10 Covariance Test Statistics"""


def covariance(S, p):
    """Measures the strength of the lagged correlation

    Parameters
    ----------
    S : list of int
        sequence of sample values
    p : int
        lag parameter p

    Returns
    -------
    int
        sum of the products of each element in the sequence with another element that is p positions ahead
    """
    T = 0
    for i in range(len(S) - p):
        T += S[i] * S[i + p]
    return T
