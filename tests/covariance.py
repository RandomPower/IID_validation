""" 5.1.10 Covariance Test Statistics"""

# Involves a parameter; it then asks to repeat the test for 5 different given values of the
# parameters (1,2,8,16,32). the function 'covariance' leaves the choice of the parameter, while 'covariance_test'
# performs 'covariace' on the aforementioned parameters and returns the statistic(s) T as an array


def covariace(S, p):
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


def covariance_test(S):
    p = [1, 2, 8, 16, 32]
    T = []
    for lag in p:
        stat = covariace(S, lag)
        T.append(stat)

    return T
