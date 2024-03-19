""" 5.1.4 Number of Increases and Decreases"""

def n_increases_decreases(S):
    S_prime = []
    for i in range(0, len(S) - 1):
        if S[i] > S[i + 1]:
            S_prime.append(-1)
        else:
            S_prime.append(1)
    if len(S_prime) == 0:
        return 0

    count_plus = 0
    count_minus = 0

    for k in range(len(S_prime)):
        if S_prime[k] == -1:
            count_minus += 1
        else:
            count_plus += 1
    return max(count_minus, count_plus)


'''S = [2, 2, 2, 5, 7, 7, 9, 3, 1, 4, 4]
print(n_increases_decreases(S))'''
