""" 5.1.9 Periodicity Test Statistics"""


def periodicity(S, y):
    T = 0
    for i in range(0, len(S) - y):
        if S[i] == S[i + y]:
            T += 1
    return T
