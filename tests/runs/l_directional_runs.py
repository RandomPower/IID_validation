""" 5.1.3 Lenght of Directional Runs"""


def l_directional_runs(S):
    S_prime = []
    for i in range(0, len(S) - 1):
        if S[i] > S[i + 1]:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0

    T = 0
    current_count = 1

    for k in range(0, len(S_prime) - 1):
        if S_prime[k] == S_prime[k + 1]:
            current_count += 1
        else:
            if current_count > T:
                T = current_count
                current_count = 1

    if current_count > T:
        T = current_count

    return T
