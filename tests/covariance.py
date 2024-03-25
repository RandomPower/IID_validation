""" 5.1.10 Covariance Test Statistics"""


def covariance(S, p):
    T = 0
    for i in range(len(S) - p):
        T += S[i] * S[i + p]
    return T
